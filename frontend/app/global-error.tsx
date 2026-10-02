"use client";

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body style={{ background: "#0d1312", color: "#e8ece9", fontFamily: "sans-serif" }}>
        <main
          style={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: "24px",
          }}
        >
          <h1 style={{ fontSize: "24px", fontWeight: 500 }}>Something went wrong.</h1>
          <p style={{ marginTop: "12px", color: "#949a9a" }}>Try reloading the page.</p>
          <button
            onClick={reset}
            style={{
              marginTop: "24px",
              padding: "10px 20px",
              borderRadius: "6px",
              background: "#58b89b",
              color: "#0a100f",
              border: "none",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </main>
      </body>
    </html>
  );
}
