export default function FlashcardsPage() {
  return (
    <main className="flex min-h-[60vh] items-center justify-center px-6">
      <div className="rounded-2xl border border-border bg-background/90 px-12 py-16 text-center shadow-lg backdrop-blur-sm">
        <h1 className="font-[family-name:var(--font-playfair)] text-4xl font-bold text-foreground">
          Coming Soon
        </h1>
        <p className="mx-auto mt-4 max-w-md font-[family-name:var(--font-dm-sans)] text-base text-muted-foreground">
          I&apos;m thinking about building some sort of flashcard system into
          LeetGoat, where when you finish solving a problem, it adds a
          flashcard to your deck, and also you can write your own
          flashcards. I&apos;m still experimenting around with how this should
          work.
        </p>
        <p className="mt-6 font-[family-name:var(--font-dm-sans)] text-sm text-muted-foreground">
          &ndash; leetgoat{" "}
          <span className="inline-block text-lg animate-[wiggle_1.5s_ease-in-out_infinite]">
            🐐
          </span>
        </p>
        <a
          href="https://discord.gg/NFscUPSx"
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 inline-block font-[family-name:var(--font-dm-sans)] text-sm font-medium text-primary underline underline-offset-4 hover:text-primary/80"
        >
          Join the Discord for updates &rarr;
        </a>
      </div>
    </main>
  );
}
