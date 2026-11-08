import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { KMP, PALINDROMES, PATTERN_MATCHING, ROTATIONS, STRINGS_MISC, SUBSTRINGS, Z_FUNCTION } from "@/lib/strings";
import { EertreePicker } from "@/components/EertreePicker";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "String Templates — LeetGoat",
};

export default async function StringTemplatesPage() {
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
        <MiscTemplates title="String templates" sections={[
            { title: "Pattern matching", items: PATTERN_MATCHING },
            { title: "Z-function", items: Z_FUNCTION },
            { title: "KMP", items: KMP },
            { title: "Substrings", items: SUBSTRINGS },
            { title: "Palindromes", items: PALINDROMES, custom: <EertreePicker key="eertree" publicBase="/range-query-templates" /> },
            { title: "Rotations", items: ROTATIONS },
            { title: "Misc.", items: STRINGS_MISC },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
