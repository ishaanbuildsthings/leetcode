import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { BUBBLE_SORT } from "@/lib/bubble-sort";
import { NEXT_PERMUTATION } from "@/lib/next-permutation";
import { REROOT } from "@/lib/reroot";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Misc. Templates — LeetGoat",
};

export default async function MiscTemplatesPage() {
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
        <MiscTemplates title="Misc. templates" sections={[
            { title: "Bubble Sort", items: BUBBLE_SORT },
            { title: "Next Permutation", items: NEXT_PERMUTATION },
            { title: "Reroot DP", items: REROOT },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
