import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { OpPicker } from "@/components/OpPicker";
import { PRIMES_GITHUB, PRIMES_GROUPS } from "@/lib/primes-picker";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Prime Templates — LeetGoat",
};

export default async function PrimeTemplatesPage() {
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
      <div className="min-h-screen bg-background">
        <Nav isDev={isDev} />
        <MiscTemplates
          title="Prime templates"
          sections={[
            {
              title: "Primes",
              items: [],
              custom: (
                <OpPicker
                  key="primes"
                  title="Primes: testing, factorizing, listing, counting"
                  folder="_primes"
                  file="Primes"
                  githubUrl={PRIMES_GITHUB}
                  groups={PRIMES_GROUPS}
                  note="One big number needs no setup; the sieve ops need the sieve built first, O(N · log(log N))."
                  publicBase="/range-query-templates"
                />
              ),
            },
          ]}
          publicBase="/range-query-templates"
        />
      </div>
    </AuthProvider>
  );
}
