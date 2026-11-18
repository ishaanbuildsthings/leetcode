import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { GEOMETRY } from "@/lib/geometry";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Geometry Templates — LeetGoat",
};

export default async function GeometryTemplatesPage() {
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
        <MiscTemplates title="Geometry templates" sections={[{ title: "Geometry", items: GEOMETRY }]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
