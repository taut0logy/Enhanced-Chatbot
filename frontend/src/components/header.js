import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"
import { AuthButton } from "@/components/auth-button"
import { Button } from "@/components/ui/button"
import { History } from "lucide-react"

// Client component for navigation
function Navigation({ user }) {
  return (
    <nav className="flex items-center space-x-2">
      {user && (
        <Link href="/history">
          <Button variant="ghost" size="icon" className="w-9 px-0">
            <History className="h-5 w-5" />
            <span className="sr-only">History</span>
          </Button>
        </Link>
      )}
      <AuthButton />
      <ThemeToggle />
    </nav>
  );
}

// Server component for header
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold sm:inline-block">
              StoryGen AI
            </span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <Navigation />
        </div>
      </div>
    </header>
  )
} 