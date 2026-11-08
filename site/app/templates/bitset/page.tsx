import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { MiscTemplates } from "@/components/TemplatePicker";
import { BITSETS } from "@/lib/bitset";
import { BIT_SUMS, SOS_DP, XOR_BASIS, XOR_CONVOLUTION } from "@/lib/bit-operations";
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
        <MiscTemplates title="Bit operation & bitset templates" sections={[
            { title: "XOR basis", items: XOR_BASIS },
            { title: "AND / OR counts (SOS DP)", items: SOS_DP },
            { title: "XOR convolution", items: XOR_CONVOLUTION },
            { title: "Sums of XOR / AND / OR over pairs and subarrays", items: BIT_SUMS },
            { title: "Bitsets", items: BITSETS },
          ]} publicBase="/range-query-templates" />
      </div>
    </AuthProvider>
  );
}
