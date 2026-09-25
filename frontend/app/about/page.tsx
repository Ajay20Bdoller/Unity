"use client";

import { useEffect, useState } from "react";
import { api, type TeamMember } from "@/lib/api";
import { SiteNav } from "@/components/site-nav";

function Initial({ name }: { name: string }) {
  return (
    <div className="flex h-full w-full items-center justify-center bg-primary/15">
      <span className="font-display text-6xl text-primary">{name.charAt(0)}</span>
    </div>
  );
}

function FeaturedProfile({ member }: { member: TeamMember }) {
  return (
    <div className="grid gap-10 sm:grid-cols-[minmax(0,220px)_1fr] sm:items-start">
      <div className="aspect-square w-full overflow-hidden rounded-2xl border border-border">
        {member.photo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={member.photo_url} alt={member.full_name} className="h-full w-full object-cover" />
        ) : (
          <Initial name={member.full_name} />
        )}
      </div>
      <div>
        <p className="text-sm font-medium uppercase tracking-wide text-accent">
          {member.role_title}
        </p>
        <h2 className="mt-2 font-display text-3xl font-medium text-ink sm:text-4xl">
          {member.full_name}
        </h2>
        {member.bio && (
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted">{member.bio}</p>
        )}
        {member.linkedin_url && (
          <a
            href={member.linkedin_url}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
          >
            Connect on LinkedIn →
          </a>
        )}
      </div>
    </div>
  );
}

function TeamGridCard({ member }: { member: TeamMember }) {
  return (
    <div className="border-t border-border pt-5">
      <div className="h-16 w-16 overflow-hidden rounded-full border border-border">
        {member.photo_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={member.photo_url} alt={member.full_name} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-primary/15">
            <span className="font-display text-xl text-primary">{member.full_name.charAt(0)}</span>
          </div>
        )}
      </div>
      <h3 className="mt-3 font-medium text-ink">{member.full_name}</h3>
      <p className="text-sm text-muted">{member.role_title}</p>
      {member.bio && <p className="mt-2 text-sm leading-relaxed text-muted">{member.bio}</p>}
      {member.linkedin_url && (
        <a
          href={member.linkedin_url}
          target="_blank"
          rel="noreferrer"
          className="mt-2 inline-block text-xs font-medium text-primary hover:underline"
        >
          LinkedIn →
        </a>
      )}
    </div>
  );
}

export default function AboutUsPage() {
  const [team, setTeam] = useState<TeamMember[] | null>(null);

  useEffect(() => {
    api.team().then(setTeam).catch(() => setTeam([]));
  }, []);

  const [featured, ...rest] = team ?? [];

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-3xl px-6 py-16 sm:py-24">
        <section className="max-w-xl">
          <h1 className="font-display text-4xl font-medium leading-[1.1] tracking-tight text-ink sm:text-5xl">
            The people building Unity
          </h1>
          <p className="mt-5 text-lg leading-relaxed text-muted">
            Unity started from a simple observation: most students never get shown the full map
            of what they could become. This is who&apos;s working on changing that.
          </p>
        </section>

        {team === null && <p className="mt-16 text-sm text-muted">Loading...</p>}

        {team !== null && team.length === 0 && (
          <p className="mt-16 text-sm text-muted">Team profiles coming soon.</p>
        )}

        {featured && (
          <section className="mt-16">
            <FeaturedProfile member={featured} />
          </section>
        )}

        {rest.length > 0 && (
          <section className="mt-16 grid gap-8 sm:grid-cols-2">
            {rest.map((member) => (
              <TeamGridCard key={member.id} member={member} />
            ))}
          </section>
        )}
      </main>
    </>
  );
}
