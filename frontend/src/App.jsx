
import { useEffect, useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const HIDDEN_LOCATIONS = new Set(["stairs 9", "stairs 9 (2)"]);

function getName(location) {
  return typeof location === "string"
    ? location
    : location?.name ?? location?.location_name ?? "";
}

function normalizeLocations(data) {
  const items = Array.isArray(data) ? data : data.locations ?? [];

  return items
    .filter(
      (item) =>
        !HIDDEN_LOCATIONS.has(getName(item).trim().toLowerCase())
    )
    .sort((a, b) =>
      getName(a).localeCompare(getName(b), undefined, {
        numeric: true,
        sensitivity: "base",
      })
    );
}

function LocationPicker({
  label,
  placeholder,
  locations,
  value,
  onChange,
  disabled,
  icon,
}) {
  const [query, setQuery] = useState(value);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  const matches = locations.filter((location) =>
    getName(location)
      .toLowerCase()
      .includes(query.trim().toLowerCase())
  );

  function handleChange(text) {
    setQuery(text);
    onChange("");
    setOpen(true);
  }

  function selectLocation(name) {
    setQuery(name);
    onChange(name);
    setOpen(false);
  }

  return (
    <div className="location-field">
      <label className="field-label">{label}</label>

      <div className={`autocomplete ${open ? "autocomplete-open" : ""}`}>
        <span className="field-icon" aria-hidden="true">
          {icon}
        </span>

        <input
          type="text"
          value={query}
          placeholder={placeholder}
          autoComplete="off"
          disabled={disabled}
          aria-label={label}
          aria-expanded={open}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onChange={(event) => handleChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") setOpen(false);

            if (event.key === "Enter" && open && matches.length > 0) {
              event.preventDefault();
              selectLocation(getName(matches[0]));
            }

            if (event.key === "ArrowDown" && matches.length > 0) {
              event.preventDefault();
              setOpen(true);
            }
          }}
        />

        <span className="search-chevron" aria-hidden="true">
          {open ? "⌃" : "⌄"}
        </span>

        {open && !disabled && (
          <div className="autocomplete-menu">
            <div className="suggestion-heading">
              {query.trim() ? "MATCHING LOCATIONS" : "CAMPUS LOCATIONS"}
            </div>

            {matches.length > 0 ? (
              matches.slice(0, 50).map((location) => {
                const name = getName(location);

                return (
                  <button
                    type="button"
                    className={`suggestion-option ${
                      value === name ? "suggestion-selected" : ""
                    }`}
                    key={name}
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => selectLocation(name)}
                  >
                    <span className="suggestion-pin">●</span>
                    <span className="suggestion-name">{name}</span>
                    {value === name && <span>✓</span>}
                  </button>
                );
              })
            ) : (
              <div className="no-suggestions">
                <span>⌕</span>
                <p>No locations found</p>
                <small>Try another room number or location name.</small>
              </div>
            )}

            {matches.length > 50 && (
              <div className="suggestion-footer">
                Type more letters to narrow your search.
              </div>
            )}
          </div>
        )}
      </div>

      {value && (
        <div className="selected-location">
          <span className="selected-check">✓</span>
          Selected: {value}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [locations, setLocations] = useState([]);
  const [start, setStart] = useState("");
  const [destination, setDestination] = useState("");
  const [accessible, setAccessible] = useState(false);
  const [loading, setLoading] = useState(true);
  const [routing, setRouting] = useState(false);
  const [error, setError] = useState("");
  const [routeResult, setRouteResult] = useState(null);

  useEffect(() => {
    async function fetchLocations() {
      try {
        const response = await fetch(`${API_BASE}/locations`);

        if (!response.ok) {
          throw new Error("Could not load campus locations.");
        }

        const data = await response.json();
        setLocations(normalizeLocations(data));
      } catch (err) {
        setError(
          "Unable to load campus locations. Please check that the backend is running."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchLocations();
  }, []);

  async function findRoute(event) {
    event.preventDefault();
    setError("");
    setRouteResult(null);

    if (!start || !destination) {
      setError("Please select both locations from the suggestions.");
      return;
    }

    if (start === destination) {
      setError("Your starting point and destination must be different.");
      return;
    }

    setRouting(true);

    try {
      const params = new URLSearchParams({
        start,
        destination,
        accessible: String(accessible),
      });

      const response = await fetch(
        `${API_BASE}/navigation?${params.toString()}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || data.message || "No route could be found."
        );
      }

      setRouteResult(data);
    } catch (err) {
      setError(
        err.message || "Unable to find a route. Please try again."
      );
      console.error(err);
    } finally {
      setRouting(false);
    }
  }

  function swapLocations() {
    const oldStart = start;
    const oldDestination = destination;

    setStart(oldDestination);
    setDestination(oldStart);
    setRouteResult(null);
    setError("");
  }

  const route = Array.isArray(routeResult?.route)
    ? routeResult.route
    : Array.isArray(routeResult?.path)
      ? routeResult.path
      : [];

  const directions = Array.isArray(routeResult?.directions)
    ? routeResult.directions
    : Array.isArray(routeResult?.instructions)
      ? routeResult.instructions
      : Array.isArray(routeResult?.steps)
        ? routeResult.steps
        : [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Smart Campus Navigator home">
          <span className="brand-icon">N</span>
          <span className="brand-copy">
            <strong>Campus<span>Nav</span></strong>
            <small>SMART CAMPUS NAVIGATOR</small>
          </span>
        </a>

        <div className="topbar-right">
          <span className="system-status">
            <span className="status-dot" />
            Campus navigation
          </span>
          <span className="topbar-symbol">⌖</span>
        </div>
      </header>

      <section className="hero">
        <div className="hero-inner">
          <div className="hero-copy">
            <span className="eyebrow">
              <span className="eyebrow-dot" />
              YOUR CAMPUS, MADE SIMPLE
            </span>

            <h1>
              Find your way.
              <br />
              <span>Get there smarter.</span>
            </h1>

            <p>
              Navigate campus rooms, labs and facilities with clear,
              step-by-step directions.
            </p>

            <div className="hero-benefits">
              <span><b>✓</b> Room-to-room directions</span>
              <span><b>✓</b> Accessible routes</span>
            </div>
          </div>

          <div className="hero-art" aria-hidden="true">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-building">
              <div className="building-roof" />
              <div className="building-body">
                <div className="building-sign">CAMPUS</div>
                <div className="building-windows">
                  {Array.from({ length: 12 }, (_, i) => (
                    <span key={i} />
                  ))}
                </div>
                <div className="building-door" />
              </div>
            </div>
            <span className="art-pin pin-one">⌖</span>
            <span className="art-pin pin-two">✓</span>
            <span className="art-route route-label">YOUR DESTINATION</span>
          </div>
        </div>
      </section>

      <main className="main-content">
        <section className="planner-card">
          <div className="section-heading">
            <div className="heading-icon">⌖</div>
            <div>
              <h2>Plan your journey</h2>
              <p>Choose where you are and where you want to go.</p>
            </div>
          </div>

          {loading && (
            <div className="loading-banner">Loading campus locations…</div>
          )}

          <form onSubmit={findRoute}>
            <div className="location-layout">
              <div className="location-stack">
                <LocationPicker
                  label="STARTING POINT"
                  placeholder="Search a room or location..."
                  locations={locations}
                  value={start}
                  onChange={setStart}
                  disabled={loading || routing}
                  icon="○"
                />

                <div className="journey-connector">
                  <span />
                  <span />
                  <span />
                </div>

                <LocationPicker
                  label="DESTINATION"
                  placeholder="Where would you like to go?"
                  locations={locations}
                  value={destination}
                  onChange={setDestination}
                  disabled={loading || routing}
                  icon="⌖"
                />
              </div>

              <button
                type="button"
                className="swap-button"
                onClick={swapLocations}
                disabled={loading || routing || (!start && !destination)}
                title="Swap starting point and destination"
                aria-label="Swap starting point and destination"
              >
                ⇅
              </button>
            </div>

            <div className="planner-divider" />

            <label className={`accessibility-card ${accessible ? "accessibility-active" : ""}`}>
              <span className="accessibility-icon">♿</span>
              <span className="accessibility-copy">
                <strong>Accessible route</strong>
                <small>Prefer elevators and avoid staircases.</small>
              </span>
              <input
                type="checkbox"
                checked={accessible}
                onChange={(event) => {
                  setAccessible(event.target.checked);
                  setRouteResult(null);
                }}
                disabled={loading || routing}
              />
              <span className="custom-switch" />
            </label>

            <button
              type="submit"
              className="find-route-button"
              disabled={loading || routing}
            >
              <span>{routing ? "Finding your route…" : "Find my route"}</span>
              <span className="button-arrow">{routing ? "…" : "→"}</span>
            </button>
          </form>

          {error && (
            <div className="error-banner" role="alert">
              <span>!</span>
              {error}
            </div>
          )}

          <div className="planner-footnote">
            <span>🔒</span>
            Choose from your campus's available locations.
          </div>
        </section>

        {!routeResult && (
          <section className="help-strip">
            <div className="help-icon">✦</div>
            <div>
              <strong>Getting around made easier</strong>
              <p>Start typing a room name or number and select a matching suggestion.</p>
            </div>
          </section>
        )}

        {routeResult && (
          <section className="results-section">
            <div className="results-heading">
              <div>
                <span className="eyebrow results-eyebrow">YOUR JOURNEY</span>
                <h2>Route found</h2>
                <p>Follow these steps to reach your destination.</p>
              </div>
              <span className="route-success">✓ Ready to go</span>
            </div>

            <div className="trip-overview">
              <div className="trip-point">
                <span className="trip-point-icon start-point">○</span>
                <div>
                  <small>STARTING POINT</small>
                  <strong>{start}</strong>
                </div>
              </div>

              <div className="trip-arrow">→</div>

              <div className="trip-point">
                <span className="trip-point-icon end-point">⌖</span>
                <div>
                  <small>DESTINATION</small>
                  <strong>{destination}</strong>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-icon">↔</span>
                <small>Horizontal distance</small>
                <strong>
                  {routeResult.distance_meters != null
                    ? `${routeResult.distance_meters} m`
                    : "—"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-icon">◷</span>
                <small>Estimated walking</small>
                <strong>
                  {routeResult.walking_time_minutes != null
                    ? `${routeResult.walking_time_minutes} min`
                    : "—"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-icon">↕</span>
                <small>Floor transitions</small>
                <strong>
                  {routeResult.vertical_transition_count ?? 0}
                </strong>
              </div>
            </div>

            {routeResult.distance_note && (
              <div className="distance-note">
                <span>ⓘ</span>
                <p>{routeResult.distance_note}</p>
              </div>
            )}

            {route.length > 0 && (
              <div className="directions-card">
                <div className="directions-heading">
                  <div>
                    <h3>Route sequence</h3>
                    <p>{route.length} locations along your journey</p>
                  </div>
                  <span className="directions-badge">
                    {accessible ? "♿ Accessible" : "Standard route"}
                  </span>
                </div>

                <ol className="route-timeline">
                  {route.map((item, index) => {
                    const name =
                      typeof item === "string"
                        ? item
                        : item.name ??
                          item.location_name ??
                          JSON.stringify(item);

                    const first = index === 0;
                    const last = index === route.length - 1;

                    return (
                      <li
                        key={`${name}-${index}`}
                        className="timeline-item"
                      >
                        <span
                          className={`timeline-marker ${
                            first ? "timeline-start" : ""
                          } ${last ? "timeline-end" : ""}`}
                        >
                          {first ? "S" : last ? "D" : index}
                        </span>
                        <div className="timeline-content">
                          <span className="timeline-caption">
                            {first
                              ? "START"
                              : last
                                ? "DESTINATION"
                                : `STEP ${index}`}
                          </span>
                          <strong>{name}</strong>
                        </div>
                      </li>
                    );
                  })}
                </ol>
              </div>
            )}

            {directions.length > 0 && (
              <div className="directions-card written-directions">
                <div className="directions-heading">
                  <div>
                    <h3>Step-by-step instructions</h3>
                    <p>Written directions for your journey</p>
                  </div>
                </div>

                <ol className="instruction-list">
                  {directions.map((item, index) => {
                    const text =
                      typeof item === "string"
                        ? item
                        : item.instruction ??
                          item.text ??
                          JSON.stringify(item);

                    return <li key={`${index}-${text}`}>{text}</li>;
                  })}
                </ol>
              </div>
            )}

            <button
              type="button"
              className="plan-another-button"
              onClick={() => {
                setRouteResult(null);
                setError("");
              }}
            >
              ← Plan another journey
            </button>
          </section>
        )}
      </main>

      <footer className="app-footer">
        <span className="footer-brand">CampusNav</span>
        <span>Smart Campus Navigator · Indoor directions</span>
      </footer>
    </div>
  );
}
