import "./globals.css";

export const metadata = {
  title: "AI Farming Environment Simulator (OpenEnv)",
  description:
    "An OpenEnv-style farming environment for AI agents. Agents learn using the reset(), step(), and state() APIs.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

