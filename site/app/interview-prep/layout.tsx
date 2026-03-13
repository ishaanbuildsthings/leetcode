import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import { Nav } from "@/components/Nav";
import { AuthProvider } from "@/contexts/AuthContext";
import { InterviewPrepTabs } from "@/components/InterviewPrepTabs";
import { GoatModeWrapper } from "@/components/GoatModeWrapper";

export default async function InterviewPrepLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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
      <GoatModeWrapper>
        <Nav activePath="/interview-prep" isDev={isDev} />
        <div className="pt-16">
          <InterviewPrepTabs />
          {children}
        </div>
      </GoatModeWrapper>
    </AuthProvider>
  );
}
