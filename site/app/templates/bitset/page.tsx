import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { BitOpsCards } from "@/components/BitOpsCards";
import { BIT_OPS_CARDS } from "@/lib/bit-operations";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata = {
  title: "Bit Operation & Bitset Templates — LeetGoat",
};

export default async function BitsetTemplatesPage() {
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
        <BitOpsCards title="Bit operation & bitset templates" cards={BIT_OPS_CARDS} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
