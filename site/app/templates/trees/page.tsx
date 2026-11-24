import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { TREE_CENTROIDS, TREE_EDGE_LISTS, TREE_HASHING } from "@/lib/trees";
import { REROOT } from "@/lib/reroot";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Tree Helper Templates — LeetGoat",
};

export default async function TreeTemplatesPage() {
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
        <MiscTemplates title="Tree helper templates" sections={[
            { title: "Edge lists", items: TREE_EDGE_LISTS },
            { title: "Centroid", items: TREE_CENTROIDS },
            { title: "Reroot DP", items: REROOT },
            { title: "Hashing", items: TREE_HASHING },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
