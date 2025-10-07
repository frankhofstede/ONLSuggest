import { useState, useEffect } from 'react'
import apiClient from './api/client'

interface HealthStatus {
  status: string
  version: string
  service: string
}

interface DatabaseStatus {
  database: string
  gemeentes: number
  services: number
  status: string
}

interface RedisStatus {
  redis: string
  test_value: string
  status: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [database, setDatabase] = useState<DatabaseStatus | null>(null)
  const [redis, setRedis] = useState<RedisStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch health status
        const healthResponse = await apiClient.get<HealthStatus>('/health')
        setHealth(healthResponse.data)

        // Fetch database status
        const dbResponse = await apiClient.get<DatabaseStatus>('/api/test/db')
        setDatabase(dbResponse.data)

        // Fetch Redis status
        const redisResponse = await apiClient.get<RedisStatus>('/api/test/redis')
        setRedis(redisResponse.data)

        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch API data')
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded">
          <strong className="font-bold">Error: </strong>
          <span>{error}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
          ONLSuggest - Full Stack Integration Test
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Health Status Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">API Health</h2>
            {health && (
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Status:</span>{' '}
                  <span className="text-green-600">{health.status}</span>
                </p>
                <p className="text-sm">
                  <span className="font-medium">Version:</span> {health.version}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Service:</span> {health.service}
                </p>
              </div>
            )}
          </div>

          {/* Database Status Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Database</h2>
            {database && (
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Status:</span>{' '}
                  <span className="text-green-600">{database.database}</span>
                </p>
                <p className="text-sm">
                  <span className="font-medium">Gemeentes:</span> {database.gemeentes}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Services:</span> {database.services}
                </p>
              </div>
            )}
          </div>

          {/* Redis Status Card */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Redis Cache</h2>
            {redis && (
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Status:</span>{' '}
                  <span className="text-green-600">{redis.redis}</span>
                </p>
                <p className="text-sm">
                  <span className="font-medium">Test:</span>{' '}
                  <span className="text-gray-600 italic">{redis.test_value}</span>
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 bg-green-50 border-l-4 border-green-500 p-4">
          <p className="text-green-700 font-medium">
            ✅ Full stack integration successful!
          </p>
          <p className="text-green-600 text-sm mt-1">
            Frontend (React + Vite) → Backend (FastAPI) → Database (PostgreSQL) + Cache (Redis)
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
