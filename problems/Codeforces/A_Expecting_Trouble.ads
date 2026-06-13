with Ada.Text_IO; use Ada.Text_IO;

procedure Main is
   package LF_IO is new Ada.Text_IO.Float_IO (Long_Float);
   use LF_IO;

   Buffer : String (1 .. 100_000);
   Last   : Natural := 0;
   P      : Long_Float;
   Expected_Bad_Days : Long_Float := 0.0;
begin
   Get_Line (Buffer, Last);
   declare
      S : constant String := Buffer (1 .. Last);
   begin
      LF_IO.Get (P);

      for I in S'Range loop
         if S (I) = '1' then
            Expected_Bad_Days := Expected_Bad_Days + 1.0;
         elsif S (I) = '?' then
            Expected_Bad_Days := Expected_Bad_Days + P;
         end if;
      end loop;

      LF_IO.Put (Expected_Bad_Days / Long_Float (S'Length), Fore => 0, Aft => 5, Exp => 0);
      New_Line;
   end;
end Main;