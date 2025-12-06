import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  createRouter,
  RouterProvider,
  createRootRoute,
  createRoute,
  Outlet,
} from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import '@/index.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

// Create the root route
const rootRoute = createRootRoute({
  component: () => (
    <>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">
                  VCF HCX Automator
                </h1>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </>
  ),
})

// Create the index route
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: function Index() {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to VCF HCX Automator
            </h2>
            <p className="text-gray-600 mb-8">
              Manage your VMware HCX workflows with ease
            </p>
            <div className="space-x-4">
              <a
                href="/sites"
                className="inline-block bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
              >
                View Sites
              </a>
              <a
                href="/migrations"
                className="inline-block bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors"
              >
                Manage Migrations
              </a>
            </div>
          </div>
        </div>
      </div>
    )
  },
})

// Create the sites route
const sitesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/sites',
  component: function Sites() {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">HCX Sites</h2>
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <p className="text-gray-600">Sites management coming soon...</p>
          </div>
        </div>
      </div>
    )
  },
})

// Create the migrations route
const migrationsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/migrations',
  component: function Migrations() {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Migration Management</h2>
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <p className="text-gray-600">Migration management coming soon...</p>
          </div>
        </div>
      </div>
    )
  },
})

// Create the router
const router = createRouter({
  routeTree: rootRoute.addChildren([indexRoute, sitesRoute, migrationsRoute]),
})

// Register the router for TypeScript
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

// Render the app
const rootElement = document.getElementById('root')!
ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
)