Your target is {target}. You have access to the recon agent, the DAST agent, and the exploitation agent. For this sample run: (1) use the recon agent to log in and explore the application (username: "mr_robot", password: "elliot123") and enumerate every endpoint and input point; (2) focus exclusively on cross site scripting — use the DAST agent to test EVERY endpoint and parameter recon identifies, not just the first one that looks promising; (3) for each endpoint DAST confirms as vulnerable, use the exploitation agent to demonstrate impact.

Your objectives, in priority order:
1. Identify every endpoint and parameter vulnerable to XSS — do not stop after the first one is found.
2. For each confirmed XSS vulnerability, who a proof of concept and explain the impact.
