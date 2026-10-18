import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [locations, setLocations] = useState([])
  const [start, setStart] = useState('')
  const [destination, setDestination] = useState('')

  const [loading, setLoading] = useState(true)
  const [routing, setRouting] = useState(false)

  const [error, setError] = useState('')
  const [routeResult, setRouteResult] = useState(null)

  // Load campus locations from the backend
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch(`${API_URL}/locations`)

        if (!response.ok) {
          throw new Error('Failed to load campus locations.')
        }

        const data = await response.json()
        setLocations(data.locations || [])
      } catch (err) {
        setError(
          err.message ||
            'Could not connect to the navigation server.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchLocations()
  }, [])

  // Find a route using the FastAPI backend
  const handleFindRoute = async () => {
    if (!start || !destination) {
      setError(
        'Please select both starting location and destination.'
      )
      setRouteResult(null)
      return
    }

    if (start === destination) {
      setError(
        'Starting location and destination cannot be the same.'
      )
      setRouteResult(null)
      return
    }

    setError('')
    setRouteResult(null)
    setRouting(true)

    try {
      const params = new URLSearchParams({
        start,
        destination,
        accessible: 'false',
      })

      const response = await fetch(
        `${API_URL}/navigation?${params.toString()}`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to find a route.'
        )
      }

      setRouteResult(data)
    } catch (err) {
      setError(
        err.message ||
          'Could not connect to the navigation server.'
      )
    } finally {
      setRouting(false)
    }
  }

  // Reset the current navigation search
  const handleReset = () => {
    setStart('')
    setDestination('')
    setRouteResult(null)
    setError('')
  }

  return (
    <main className="app">
      <section className="hero-section">
        <div className="hero-content">
          <p className="eyebrow">SMART CAMPUS</p>

          <h1>Smart Campus Navigator</h1>

          <p className="description">
            Find classrooms, laboratories, offices, and facilities
            with intelligent indoor campus navigation.
          </p>

          <div className="navigation-card">
            {/* Starting location */}
            <div className="field">
              <label htmlFor="start">
                Starting Location
              </label>

              <select
                id="start"
                value={start}
                onChange={(event) => {
                  setStart(event.target.value)
                  setError('')
                  setRouteResult(null)
                }}
                disabled={loading || routing}
              >
                <option value="">
                  {loading
                    ? 'Loading locations...'
                    : 'Select starting location'}
                </option>

                {locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.name}
                  >
                    {location.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Destination */}
            <div className="field">
              <label htmlFor="destination">
                Destination
              </label>

              <select
                id="destination"
                value={destination}
                onChange={(event) => {
                  setDestination(event.target.value)
                  setError('')
                  setRouteResult(null)
                }}
                disabled={loading || routing}
              >
                <option value="">
                  {loading
                    ? 'Loading locations...'
                    : 'Select destination'}
                </option>

                {locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.name}
                  >
                    {location.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Error message */}
            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
            )}

            {/* Find route button */}
            <button
              className="route-button"
              onClick={handleFindRoute}
              disabled={loading || routing}
            >
              {loading
                ? 'Loading Locations...'
                : routing
                  ? 'Finding Route...'
                  : 'Find Route'}
            </button>

            {/* Route results */}
            {routeResult && (
              <section
                className="route-result"
                aria-live="polite"
              >
                <h2>Your Route</h2>

                <div className="route-endpoints">
                  <p>
                    <strong>From:</strong>{' '}
                    {routeResult.start}
                  </p>

                  <p>
                    <strong>To:</strong>{' '}
                    {routeResult.destination}
                  </p>
                </div>

                {/* Distance and walking time */}
                <div className="route-summary">
                  <div className="summary-item">
                    <span className="summary-label">
                      Distance
                    </span>

                    <span className="summary-value">
                      {routeResult.distance_meters} m
                    </span>
                  </div>

                  <div className="summary-item">
                    <span className="summary-label">
                      Walking Time
                    </span>

                    <span className="summary-value">
                      {routeResult.walking_time_minutes} min
                    </span>
                  </div>
                </div>

                {/* Locations in the route */}
                <h3>Route</h3>

                {Array.isArray(routeResult.route) &&
                routeResult.route.length > 0 ? (
                  <ol className="route-list">
                    {routeResult.route.map(
                      (location, index) => (
                        <li key={`${location}-${index}`}>
                          {location}
                        </li>
                      )
                    )}
                  </ol>
                ) : (
                  <p>No route details available.</p>
                )}

                {/* Step-by-step directions */}
                <h3>Directions</h3>

                {Array.isArray(routeResult.directions) &&
                routeResult.directions.length > 0 ? (
                  <ol className="directions-list">
                    {routeResult.directions.map(
                      (direction, index) => (
                        <li key={`${direction}-${index}`}>
                          {direction}
                        </li>
                      )
                    )}
                  </ol>
                ) : (
                  <p>No directions available.</p>
                )}

                <button
                  className="reset-button"
                  onClick={handleReset}
                >
                  Find Another Route
                </button>
              </section>
            )}
          </div>

          <p className="footer-text">
            Indoor navigation made simple.
          </p>
        </div>
      </section>
    </main>
  )
}

export default App