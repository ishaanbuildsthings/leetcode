import { createClient } from "@/lib/supabase/server";
import { prisma } from "@/lib/prisma";
import * as problemService from "@/lib/services/problem.service";
import { transformProblemWithRelations } from "@/lib/transforms";
import { ProblemsList } from "@/components/ProblemsList";
import { AuthProvider } from "@/contexts/AuthContext";

export default async function HomePage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  let userId: string | null = null;
  let isAdmin = false;
  
  if (user) {
    userId = user.id;
    const dbUser = await prisma.users.findUnique({ where: { id: user.id } });
    isAdmin = dbUser?.is_admin ?? false;
  }
  
  const problemsData = await problemService.unsafe_listProblems();
  const problems = problemsData.map(transformProblemWithRelations);

  return (
    <AuthProvider value={{ userId, isAdmin }}>
      <ProblemsList problems={problems} />
    </AuthProvider>
  );
}
