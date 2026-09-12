import Link from "next/link";
import { Button } from "@/components/ui/button";

const journey = [
  { step: "Discover", detail: "See careers you didn't know existed." },
  { step: "Understand", detail: "Learn what the work actually involves." },
  { step: "Explore", detail: "Compare subjects, degrees, and paths." },
  { step: "Assess", detail: "Get a sense of what fits you — not a verdict." },
  { step: "Learn", detail: "Pick up real skills, free, at your pace." },
  { step: "Get guidance", detail: "Talk to a mentor when you need one." },
  { step: "Track progress", detail: "Watch how far you've come." },
];

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-16">
      <header className="flex items-center justify-between">
        <span className="text-lg font-semibold text-ink">Unity</span>
        <nav className="flex gap-3">
          <Link href="/login">
            <Button variant="secondary">Log in</Button>
          </Link>
          <Link href="/register">
            <Button>Get started</Button>
          </Link>
        </nav>
      </header>

      <section className="mt-20 max-w-2xl">
        <h1 className="text-4xl font-semibold leading-tight text-ink sm:text-5xl">
          A career companion for students who haven’t been shown the map yet.
        </h1>
        <p className="mt-5 max-w-xl text-lg text-muted">
          Unity helps school students discover careers, understand what they
          involve, and learn the skills to get there — starting wherever they
          are, in the language they’re comfortable in.
        </p>
        <div className="mt-8">
          <Link href="/register">
            <Button className="px-6 py-3 text-base">Start exploring</Button>
          </Link>
        </div>
      </section>

      <section className="mt-24">
        <ol className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {journey.map((item, i) => (
            <li key={item.step} className="border-l-2 border-primary/30 pl-4">
              <span className="text-sm text-muted">{i + 1}</span>
              <h2 className="mt-1 font-medium text-ink">{item.step}</h2>
              <p className="mt-1 text-sm text-muted">{item.detail}</p>
            </li>
          ))}
        </ol>
      </section>
    </main>
  );
}
