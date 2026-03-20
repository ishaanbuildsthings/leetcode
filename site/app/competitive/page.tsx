import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";

export default async function CompetitivePage() {
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
      <div
        className="min-h-screen bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url('/goat-field-bg.jpg')" }}
      >
        <Nav activePath="/competitive" isDev={isDev} />
        <main className="flex min-h-screen items-center justify-center px-6 pt-16">
          <div className="rounded-2xl border border-border bg-background/90 px-12 py-16 text-center shadow-lg backdrop-blur-sm">
            <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold text-foreground">
              Coming Soon
            </h1>
            <p className="mx-auto mt-4 max-w-md font-[family-name:var(--font-dm-sans)] text-base text-muted-foreground">
              I&apos;ll build this section when I reach 2000+ rating on
              Codeforces.
            </p>
            <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
              &ndash; leetgoat{" "}
              <span className="inline-block text-lg animate-[wiggle_1.5s_ease-in-out_infinite]">
                🐐
              </span>
            </p>
            <a
              href="https://discord.gg/NFscUPSx"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-6 inline-block font-[family-name:var(--font-dm-sans)] text-sm font-medium text-primary underline underline-offset-4 hover:text-primary/80"
            >
              Join the Discord for updates &rarr;
            </a>
          </div>
        </main>
      </div>
    </AuthProvider>
  );
}
