import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { BUBBLE_SORT } from "@/lib/bubble-sort";
import { CHESS } from "@/lib/chess";
import { BISECTS } from "@/lib/bisects";
import { STACKS } from "@/lib/stacks";
import { MOS } from "@/lib/mos";
import { LIS } from "@/lib/lis";
import { HASH_TABLES } from "@/lib/hash-tables";
import { NEXT_PERMUTATION } from "@/lib/next-permutation";
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
            { title: "Hash Tables", items: HASH_TABLES },
            { title: "Stacks", items: STACKS },
            { title: "Bisects", items: BISECTS },
            { title: "Mo's", items: MOS },
            { title: "Longest Increasing Subsequence", items: LIS },
            { title: "Next Permutation", items: NEXT_PERMUTATION },
            { title: "Bubble Sort", items: BUBBLE_SORT },
            { title: "Chess", items: CHESS },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
