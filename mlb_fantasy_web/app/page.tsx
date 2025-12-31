import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between whitespace-nowrap border-b border-border bg-background/95 backdrop-blur px-6 py-4 lg:px-20">
        <div className="flex items-center gap-4">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary/20 text-primary">
            <span className="material-symbols-outlined text-xl">sports_baseball</span>
          </div>
          <h2 className="text-lg font-bold leading-tight tracking-tight">Fantasy AI Scout</h2>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="#features"
            className="hidden h-10 items-center justify-center px-4 text-sm font-bold text-muted-foreground hover:text-primary transition-colors sm:flex"
          >
            How it Works
          </Link>
          <Button asChild>
            <Link href="/login">Login</Link>
          </Button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center w-full">
        {/* Hero Section */}
        <section className="w-full max-w-[1280px] px-6 lg:px-20 py-12 lg:py-20">
          <div className="flex flex-col gap-12 lg:flex-row lg:items-center lg:gap-16">
            {/* Text Content */}
            <div className="flex flex-col gap-8 lg:w-1/2">
              <div className="flex flex-col gap-4 text-left">
                <div className="inline-flex w-fit items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-wide text-primary">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
                  </span>
                  New Season Ready
                </div>
                <h1 className="text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl">
                  Moneyball, <br />
                  <span className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
                    powered by AI.
                  </span>
                </h1>
                <p className="max-w-lg text-lg font-normal leading-relaxed text-muted-foreground sm:text-xl">
                  Connect your Yahoo Sports league. Get instant AI scouting reports, uncover hidden
                  waiver wire gems, and optimize your lineup daily.
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Button size="lg" className="h-12 min-w-[160px] text-base shadow-lg shadow-primary/25" asChild>
                  <Link href="/signup">Start Scouting for Free</Link>
                </Button>
                <Button variant="outline" size="lg" className="h-12 min-w-[160px] text-base" asChild>
                  <Link href="/dashboard">View Demo</Link>
                </Button>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="material-symbols-outlined text-base text-emerald-500">check_circle</span>
                <span>Official Yahoo Sports Integration</span>
                <span className="mx-2 text-border">|</span>
                <span className="material-symbols-outlined text-base text-yellow-500">star</span>
                <span>Trusted by 10,000+ Managers</span>
              </div>
            </div>

            {/* Hero Image */}
            <div className="relative lg:w-1/2">
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-primary to-cyan-400 opacity-20 blur-2xl"></div>
              <div className="relative aspect-[4/3] w-full overflow-hidden rounded-xl border border-border bg-card shadow-2xl">
                {/* Placeholder gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-background"></div>
                <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent"></div>

                {/* Floating UI Card Mockup */}
                <div className="absolute inset-x-6 bottom-6 rounded-lg border border-border bg-card/90 p-4 backdrop-blur-md shadow-xl">
                  <div className="mb-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex size-10 items-center justify-center rounded-full bg-muted text-xs font-bold text-muted-foreground">
                        SO
                      </div>
                      <div>
                        <div className="text-sm font-bold">Shohei Ohtani</div>
                        <div className="text-xs font-medium text-primary">98% Match Rating</div>
                      </div>
                    </div>
                    <span className="material-symbols-outlined text-primary">trending_up</span>
                  </div>
                  <div className="mb-1 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-1.5 rounded-full bg-primary" style={{ width: "92%" }}></div>
                  </div>
                  <div className="flex justify-between text-[10px] font-mono uppercase tracking-wider text-muted-foreground">
                    <span>Proj. HR: 45</span>
                    <span>Proj. SB: 25</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="w-full border-y border-border bg-secondary/50">
          <div className="mx-auto w-full max-w-[1280px] px-6 py-20 lg:px-20">
            <div className="mx-auto mb-16 flex max-w-3xl flex-col gap-4 text-center">
              <h2 className="text-3xl font-bold leading-tight tracking-tight sm:text-4xl">
                Why use Fantasy AI Scout?
              </h2>
              <p className="text-lg text-muted-foreground">
                Leverage advanced machine learning to build a championship roster without spending
                hours in spreadsheets.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              {/* Feature 1 */}
              <div className="group flex flex-col gap-6 rounded-2xl border border-border bg-card p-8 transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                <div className="flex size-14 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <span className="material-symbols-outlined text-3xl">psychology</span>
                </div>
                <div className="flex flex-col gap-3">
                  <h3 className="text-xl font-bold">AI Scouting Reports</h3>
                  <p className="leading-relaxed text-muted-foreground">
                    Stop guessing. Let our neural network analyze batter vs. pitcher matchups using
                    historical data and predictive modeling.
                  </p>
                </div>
              </div>

              {/* Feature 2 */}
              <div className="group flex flex-col gap-6 rounded-2xl border border-border bg-card p-8 transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                <div className="flex size-14 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <span className="material-symbols-outlined text-3xl">link</span>
                </div>
                <div className="flex flex-col gap-3">
                  <h3 className="text-xl font-bold">Seamless Integration</h3>
                  <p className="leading-relaxed text-muted-foreground">
                    Directly sync your leagues and rosters from Yahoo Sports. Updates in real-time
                    as your league mates make moves.
                  </p>
                </div>
              </div>

              {/* Feature 3 */}
              <div className="group flex flex-col gap-6 rounded-2xl border border-border bg-card p-8 transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
                <div className="flex size-14 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <span className="material-symbols-outlined text-3xl">diamond</span>
                </div>
                <div className="flex flex-col gap-3">
                  <h3 className="text-xl font-bold">Waiver Wire Gems</h3>
                  <p className="leading-relaxed text-muted-foreground">
                    Find the breakout players before anyone else. Our algorithm identifies
                    undervalued assets based on underlying metrics.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full max-w-[1280px] px-6 py-24 lg:px-20">
          <div className="relative overflow-hidden rounded-3xl bg-primary px-6 py-16 sm:px-12 sm:py-20 lg:px-24">
            {/* Background Effects */}
            <div className="absolute left-0 top-0 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-white/10 blur-3xl"></div>
            <div className="absolute bottom-0 right-0 translate-x-1/3 translate-y-1/3 h-96 w-96 rounded-full bg-black/20 blur-3xl"></div>
            <div className="relative z-10 flex flex-col items-center justify-center gap-8 text-center">
              <div className="flex max-w-2xl flex-col gap-4">
                <h2 className="text-3xl font-black leading-tight tracking-tight text-white sm:text-4xl md:text-5xl">
                  Ready to win your league?
                </h2>
                <p className="text-lg font-medium text-blue-100 sm:text-xl">
                  Join the data revolution. It takes less than 2 minutes to import your team and
                  start getting recommendations.
                </p>
              </div>
              <div className="flex w-full flex-col items-center justify-center gap-4 sm:flex-row">
                <Button
                  size="lg"
                  variant="secondary"
                  className="h-14 min-w-[200px] gap-3 rounded-xl bg-white px-8 text-lg font-bold text-primary shadow-xl hover:bg-blue-50"
                  asChild
                >
                  <Link href="/signup">
                    <span className="material-symbols-outlined">sports_esports</span>
                    Connect Yahoo Team
                  </Link>
                </Button>
              </div>
              <p className="text-sm text-blue-200/80">No credit card required for basic scouting.</p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border bg-background px-6 py-12 lg:px-20">
        <div className="mx-auto flex max-w-[1280px] flex-col items-center justify-between gap-8 md:flex-row">
          <div className="flex items-center gap-3">
            <div className="flex size-6 items-center justify-center rounded bg-primary/20 text-primary">
              <span className="material-symbols-outlined text-sm">sports_baseball</span>
            </div>
            <span className="text-sm font-bold">Fantasy AI Scout</span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-8">
            <Link
              href="#"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Terms of Service
            </Link>
            <Link
              href="#"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Support
            </Link>
          </div>
          <p className="text-sm text-muted-foreground">© 2024 Fantasy AI Scout.</p>
        </div>
      </footer>
    </div>
  );
}
