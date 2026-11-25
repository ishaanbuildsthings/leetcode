import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { OpPicker } from "@/components/OpPicker";
import { FIBONACCI_GROUPS, MATH_GITHUB, MODCALC_GROUPS, STIRLING_GROUPS } from "@/lib/math-pickers";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Math Templates — LeetGoat",
};

export default async function MathTemplatesPage() {
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
        <MiscTemplates title="Math templates" sections={[
            {
              title: "Counting (ModCalc)",
              items: [],
              custom: (
                <OpPicker
                  key="modcalc"
                  title="ModCalc"
                  folder="_combinatorics"
                  file="ModCalc"
                  githubUrl={MATH_GITHUB}
                  groups={MODCALC_GROUPS}
                  note="Mod 10^9 + 7 unless you pass another. The factorial tables grow on demand: no size to pick."
                  publicBase="/range-query-templates"
                />
              ),
            },
            {
              title: "Stirling",
              items: [],
              custom: (
                <OpPicker
                  key="stirling"
                  title="Stirling numbers (distinct items, no empty buckets)"
                  folder="_combinatorics"
                  file="Stirling"
                  githubUrl={MATH_GITHUB}
                  groups={STIRLING_GROUPS}
                  note="Mod 10^9 + 7 unless you pass another."
                  publicBase="/range-query-templates"
                />
              ),
            },
            {
              title: "Fibonacci",
              items: [],
              custom: (
                <OpPicker
                  key="fibonacci"
                  title="Fibonacci"
                  folder="_combinatorics"
                  file="Fibonacci"
                  githubUrl={MATH_GITHUB}
                  groups={FIBONACCI_GROUPS}
                  publicBase="/range-query-templates"
                />
              ),
            },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
