import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";

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
    <>
      <SiteNav />
      <main className="mx-auto flex max-w-5xl flex-col px-6 py-16 sm:py-24">
        <section className="max-w-2xl">
          <h1 className="font-display text-4xl font-medium leading-[1.1] tracking-tight text-ink sm:text-6xl">
            A career companion for students who haven&rsquo;t been shown the
            map yet.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            Unity helps school students discover careers, understand what
            they involve, and learn the skills to get there — starting
            wherever they are, in the language they&rsquo;re comfortable in.
          </p>
          <div className="mt-8 flex items-center gap-4">
            <Link href="/register">
              <Button className="px-6 py-3 text-base">Start exploring</Button>
            </Link>
            <Link href="/careers" className="text-sm font-medium text-ink hover:text-primary">
              Browse careers first →
            </Link>
          </div>
        </section>

        <section className="mt-28">
          <ol className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
            {journey.map((item, i) => (
              <li key={item.step} className="border-l-2 border-primary/30 pl-4">
                <span className="font-display text-2xl text-primary/70">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h2 className="mt-2 font-medium text-ink">{item.step}</h2>
                <p className="mt-1 text-sm leading-relaxed text-muted">{item.detail}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>
    </>
  );
}
