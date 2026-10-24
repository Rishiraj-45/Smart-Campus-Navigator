import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const HIDDEN_LOCATIONS = new Set(["stairs 9", "stairs 9 (2)"]);

function getName(item) {
  if (typeof item === "string") return item;

  return (
    item?.name ??
    item?.location_name ??
    item?.title ??
    ""
  );
}

function getId(item) {
  if (typeof item === "string") return item;
  return item?.id ?? getName(item);
}

function normalize(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function formatDistance(value) {
  const meters = Number(value);

  if (!Number.isFinite(meters) || meters < 0) return null;

  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2).replace(/\.?0+$/, "")} km`;
  }

  return `${Math.round(meters)} m`;
}

function formatTime(value) {
  const minutes = Number(value);

  if (!Number.isFinite(minutes) || minutes < 0) return null;
  if (minutes < 1) return "Less than 1 minute";

  const total = Math.round(minutes);
  const hours = Math.floor(total / 60);
  const remaining = total % 60;

  if (hours === 0) return `${total} min`;

  return remaining
    ? `${hours} hr ${remaining} min`
    : `${hours} hr`;
}

function getArray(data, keys) {
  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }

  return [];
}

function getStepText(step) {
  if (typeof step === "string") return step;

  return (
    step?.instruction ??
    step?.direction ??
    step?.description ??
    step?.text ??
    step?.name ??
    ""
  );
}

function getErrorMessage(error) {
  if (error instanceof TypeError) {
    return "Could not connect to the server. Please check that the backend is running.";
  }

  return error?.message || "Something went wrong. Please try again.";
}

export default function App() {
  const [locations, setLocations] = useState([]);
  const [start, setStart] = useState("");
  const [destination, setDestination] = useState("");
  const [startQuery, setStartQuery] = useState("");
  const [destinationQuery, setDestinationQuery] = useState("");
  const [activePicker, setActivePicker] = useState("");
  const [accessible, setAccessible] = useState(false);

  const [loadingLocations, setLoadingLocations] = useState(true);
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [locationsError, setLocationsError] = useState("");
  const [routeError, setRouteError] = useState("");
  const [route, setRoute] = useState(null);

  const loadLocations = useCallback(async (signal) => {
    setLoadingLocations(true);
    setLocationsError("");

    try {
      const response = await fetch(`${API_BASE}/locations`, { signal });

      if (!response.ok) {
        throw new Error(`Unable to load locations (${response.status}).`);
      }

      const data = await response.json();
      const list = Array.isArray(data)
        ? data
        : data.locations ?? data.results ?? [];

      setLocations(list);
    } catch (error) {
      if (error.name !== "AbortError") {
        setLocationsError(getErrorMessage(error));
      }
    } finally {
      if (!signal?.aborted) {
        setLoadingLocations(false);
      }
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    loadLocations(controller.signal);

    return () => controller.abort();
  }, [loadLocations]);

  const sortedLocations = useMemo(() => {
    const seen = new Set();

    return locations
      .filter((item) => {
        const name = normalize(getName(item));

        if (
          !name ||
          HIDDEN_LOCATIONS.has(name) ||
          seen.has(name)
        ) {
          return false;
        }

        seen.add(name);
        return true;
      })
      .sort((a, b) =>
        getName(a).localeCompare(getName(b), undefined, {
          numeric: true,
          sensitivity: "base",
        })
      );
  }, [locations]);

  const getOptions = useCallback(
    (query, selected) => {
      const search = normalize(query);

      return sortedLocations
        .filter((item) => {
          const name = normalize(getName(item));

          return (
            name === normalize(selected) ||
            !search ||
            name.includes(search)
          );
        })
        .slice(0, 50);
    },
    [sortedLocations]
  );

  const startOptions = useMemo(
    () => getOptions(startQuery, start),
    [getOptions, startQuery, start]
  );

  const destinationOptions = useMemo(
    () => getOptions(destinationQuery, destination),
    [getOptions, destinationQuery, destination]
  );

  function chooseLocation(which, item) {
    const name = getName(item);

    if (which === "start") {
      setStart(name);
      setStartQuery(name);
    } else {
      setDestination(name);
      setDestinationQuery(name);
    }

    setActivePicker("");
    setRoute(null);
    setRouteError("");
  }

  function updateLocation(which, value) {
    if (which === "start") {
      setStartQuery(value);
      setStart(value);
    } else {
      setDestinationQuery(value);
      setDestination(value);
    }

    setActivePicker(which);
    setRoute(null);
    setRouteError("");
  }

  function swapLocations() {
    setStart(destination);
    setDestination(start);
    setStartQuery(destination);
    setDestinationQuery(start);
    setRoute(null);
    setRouteError("");
  }

  function clearForm() {
    setStart("");
    setDestination("");
    setStartQuery("");
    setDestinationQuery("");
    setActivePicker("");
    setRoute(null);
    setRouteError("");
  }

  async function findRoute(event) {
    event.preventDefault();
    setRoute(null);
    setRouteError("");

    if (!start.trim() || !destination.trim()) {
      setRouteError(
        "Please select both a starting point and a destination."
      );
      return;
    }

    if (normalize(start) === normalize(destination)) {
      setRouteError(
        "Starting point and destination must be different."
      );
      return;
    }

    setLoadingRoute(true);

    try {
      const params = new URLSearchParams({
        start: start.trim(),
        destination: destination.trim(),
        accessible: String(accessible),
      });

      const response = await fetch(
        `${API_BASE}/navigation?${params.toString()}`
      );

      let data = {};

      try {
        data = await response.json();
      } catch {
        // Handle empty or non-JSON responses below.
      }

      if (!response.ok) {
        throw new Error(
          data.detail ??
            data.message ??
            `Unable to find route (${response.status}).`
        );
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setRoute(data);
    } catch (error) {
      setRouteError(getErrorMessage(error));
    } finally {
      setLoadingRoute(false);
    }
  }

  const path = getArray(route, [
    "path",
    "route",
    "locations",
    "route_path",
  ]);

  const directions = getArray(route, [
    "directions",
    "instructions",
    "steps",
  ]);

  const distance =
    formatDistance(
      route?.distance_meters ??
        route?.distance ??
        route?.total_distance
    ) ?? route?.distance_note ?? null;

  const walkingTime = formatTime(
    route?.walking_time_minutes ??
      route?.estimated_time_minutes
  );

  const transitions =
    route?.vertical_transition_count ??
    route?.vertical_transitions ??
    null;

  const routeNote =
    route?.distance_note ??
    route?.note ??
    route?.message ??
    "";

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Campus Navigator home">
          <span className="brand-icon">C</span>
          <span>
            <strong>Campus Navigator</strong>
            <small>Indoor navigation system</small>
          </span>
        </a>
      </header>

      <main className="main-content">
        <section className="intro">
          <h1>Campus Navigator</h1>
          <p>
            Find your way around campus with simple,
            step-by-step directions.
          </p>
        </section>

        <section className="planner-card">
          <h2>Find a location</h2>

          <p className="section-description">
            Select your starting point and destination.
          </p>

          {locationsError && (
            <div className="message error" role="alert">
              <p>{locationsError}</p>
              <button
                type="button"
                className="text-button"
                onClick={() => loadLocations()}
              >
                Try again
              </button>
            </div>
          )}

          <form onSubmit={findRoute}>
            <div className="location-field">
              <label htmlFor="start-location">
                Starting point
              </label>

              <div className="input-wrap">
                <input
                  id="start-location"
                  type="text"
                  value={startQuery}
                  placeholder="Select starting location"
                  autoComplete="off"
                  onChange={(event) =>
                    updateLocation("start", event.target.value)
                  }
                  onFocus={() => setActivePicker("start")}
                  onBlur={() =>
                    window.setTimeout(
                      () => setActivePicker(""),
                      150
                    )
                  }
                  aria-autocomplete="list"
                  aria-expanded={
                    activePicker === "start" &&
                    startOptions.length > 0
                  }
                />

                {activePicker === "start" &&
                  startOptions.length > 0 && (
                    <div className="suggestions" role="listbox">
                      {startOptions.map((item) => (
                        <button
                          type="button"
                          role="option"
                          className="suggestion"
                          key={getId(item)}
                          onMouseDown={(event) =>
                            event.preventDefault()
                          }
                          onClick={() =>
                            chooseLocation("start", item)
                          }
                        >
                          {getName(item)}
                        </button>
                      ))}
                    </div>
                  )}
              </div>
            </div>

            <div className="swap-row">
              <button
                type="button"
                className="swap-button"
                onClick={swapLocations}
                aria-label="Swap starting point and destination"
              >
                ⇅ Swap locations
              </button>
            </div>

            <div className="location-field">
              <label htmlFor="destination-location">
                Destination
              </label>

              <div className="input-wrap">
                <input
                  id="destination-location"
                  type="text"
                  value={destinationQuery}
                  placeholder="Select destination"
                  autoComplete="off"
                  onChange={(event) =>
                    updateLocation(
                      "destination",
                      event.target.value
                    )
                  }
                  onFocus={() =>
                    setActivePicker("destination")
                  }
                  onBlur={() =>
                    window.setTimeout(
                      () => setActivePicker(""),
                      150
                    )
                  }
                  aria-autocomplete="list"
                  aria-expanded={
                    activePicker === "destination" &&
                    destinationOptions.length > 0
                  }
                />

                {activePicker === "destination" &&
                  destinationOptions.length > 0 && (
                    <div className="suggestions" role="listbox">
                      {destinationOptions.map((item) => (
                        <button
                          type="button"
                          role="option"
                          className="suggestion"
                          key={getId(item)}
                          onMouseDown={(event) =>
                            event.preventDefault()
                          }
                          onClick={() =>
                            chooseLocation("destination", item)
                          }
                        >
                          {getName(item)}
                        </button>
                      ))}
                    </div>
                  )}
              </div>
            </div>

            <label className="accessible-option">
              <input
                type="checkbox"
                checked={accessible}
                onChange={(event) => {
                  setAccessible(event.target.checked);
                  setRoute(null);
                }}
              />
              <span>Accessible route</span>
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={clearForm}
              >
                Clear
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={loadingRoute || loadingLocations}
              >
                {loadingRoute ? "Finding route..." : "Find Route"}
              </button>
            </div>
          </form>

          {loadingLocations && (
            <p className="loading-hint">
              Loading campus locations...
            </p>
          )}
        </section>

        {routeError && (
          <div className="message error route-error" role="alert">
            {routeError}
          </div>
        )}

        {route && (
          <section className="results-section" aria-live="polite">
            <h2>Your route</h2>

            <p className="section-description">
              Follow the directions below to reach your destination.
            </p>

            <div className="route-summary">
              <div className="summary-location">
                <span className="point-label">STARTING POINT</span>
                <strong>{start}</strong>
              </div>

              <div className="summary-arrow" aria-hidden="true">
                ↓
              </div>

              <div className="summary-location">
                <span className="point-label">DESTINATION</span>
                <strong>{destination}</strong>
              </div>
            </div>

            {(distance ||
              walkingTime ||
              transitions !== null) && (
              <div className="route-stats">
                {distance && (
                  <div className="stat">
                    <span>Distance</span>
                    <strong>{distance}</strong>
                  </div>
                )}

                {walkingTime && (
                  <div className="stat">
                    <span>Walking time</span>
                    <strong>{walkingTime}</strong>
                  </div>
                )}

                {transitions !== null && (
                  <div className="stat">
                    <span>Floor transitions</span>
                    <strong>{transitions}</strong>
                  </div>
                )}
              </div>
            )}

            {routeNote && (
              <p className="route-note">
                <strong>Note:</strong> {routeNote}
              </p>
            )}

            {path.length > 0 && (
              <div className="directions-card">
                <h3>Route sequence</h3>

                <ol className="route-list">
                  {path.map((item, index) => {
                    const name =
                      getName(item) || getStepText(item);

                    return (
                      <li key={`${name}-${index}`}>
                        <span className="route-index">
                          {index + 1}
                        </span>
                        <span>{name}</span>
                      </li>
                    );
                  })}
                </ol>
              </div>
            )}

            {directions.length > 0 && (
              <div className="directions-card">
                <h3>Step-by-step directions</h3>

                <ol className="instruction-list">
                  {directions.map((step, index) => (
                    <li key={`step-${index}`}>
                      <span className="route-index">
                        {index + 1}
                      </span>
                      <span>{getStepText(step)}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {path.length === 0 && directions.length === 0 && (
              <div className="message info">
                The server returned a route, but no written steps
                were included in its response.
              </div>
            )}

            <button
              type="button"
              className="secondary-button clear-route"
              onClick={() => {
                setRoute(null);
                setRouteError("");
              }}
            >
              Clear route results
            </button>
          </section>
        )}
      </main>

      <footer className="page-footer">
        Campus Navigator · Indoor navigation system
      </footer>
    </div>
  );
}