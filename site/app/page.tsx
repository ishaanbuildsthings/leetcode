import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import Link from "next/link";
import { GoatModeToggle } from "@/components/GoatModeToggle";

export default async function HomePage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  let userId: string | null = null;
  let isAdmin = false;

  if (user) {
    userId = user.id;
    const dbUser = await prisma.users.findUnique({ where: { id: user.id } });
    isAdmin = dbUser?.is_admin ?? false;
  }

  const isDev = process.env.NODE_ENV === "development";

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <GoatModeToggle>
        <Nav activePath="/" isDev={isDev} />

        {/* Hero */}
        <section
          className="relative flex min-h-screen items-start pt-28 lg:items-center lg:pt-16"
        >

          <div className="relative mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-12 px-6 lg:grid-cols-2">
            {/* Left — headline + CTA */}
            <div>
              <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold leading-tight text-foreground sm:text-5xl">
                Learn to actually solve LeetCode problems. Not memorize them.
              </h1>

              <p className="mt-4 font-[family-name:var(--font-dm-sans)] text-lg font-semibold text-foreground" style={{ textShadow: '0 1px 8px rgba(255,255,255,0.6), 0 0 30px rgba(255,255,255,0.3)' }}>
                (from someone who&apos;s solved 3,000+ of them)
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-4">
                <Link
                  href="/interview-prep"
                  className="inline-flex items-center gap-2 rounded-lg bg-primary px-7 py-3.5 font-[family-name:var(--font-dm-sans)] text-sm font-semibold text-primary-foreground shadow-md transition-colors hover:bg-primary/90"
                >
                  Start Practicing (it&apos;s free)
                  <span aria-hidden="true">&rarr;</span>
                </Link>
                <a
                  href="https://discord.gg/ENypyH9n"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-[#5865F2] px-7 py-3.5 font-[family-name:var(--font-dm-sans)] text-sm font-semibold text-white shadow-md transition-colors hover:bg-[#4752C4]"
                >
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.095 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
                  </svg>
                  Join the Herd
                </a>
              </div>
            </div>

            {/* Right — video placeholder */}
            <div className="flex items-center justify-center">
              <div className="flex w-full max-w-lg flex-col items-center justify-center rounded-2xl border border-border bg-background/70 backdrop-blur-md aspect-video shadow-lg">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/20">
                  <svg
                    className="h-6 w-6 text-primary"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
                <p className="mt-4 text-center font-[family-name:var(--font-dm-sans)] text-sm text-foreground font-medium">
                  What I learned from solving 3,000 LeetCode problems
                </p>
                <p className="mt-1 text-center font-[family-name:var(--font-dm-sans)] text-xs text-muted-foreground">
                  Coming soon
                </p>
              </div>
            </div>
          </div>
        </section>


      </GoatModeToggle>
    </AuthProvider>
  );
}
