import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { GOLDEN_REFERENCES } from "@/lib/golden-references";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Golden References — LeetGoat",
};

export default async function GoldenReferencesPage() {
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
        <MiscTemplates title="Golden References" sections={[{ title: "Persistent Segment Tree", items: GOLDEN_REFERENCES }]} publicBase="/range-query-templates" planned={["Seg tree beats"]} />
      </div>
    </AuthProvider>
  );
}
