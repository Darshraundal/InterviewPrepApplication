import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:/Project/InterviewPrep/src/InterviewPrepPortal/Data/JsonData/questions-behavioral.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_questions = [

# ─── SELF-AWARENESS & PERFORMANCE EVALUATION ───────────────────────────────

{
  "id": "beh-009",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "very-high",
  "question": "What are your top 3 achievements in your current role that directly impacted business outcomes?",
  "answer": "<p>I always keep three stories ready for this one because it comes up a lot.</p><p><strong>First — the query performance fix in CSInvoice.</strong> The finance team ran a Monday morning report that took 8–9 minutes every single week. I noticed it during regular dev work, traced it to full table scans on the Invoices table, and added a composite covering index on ClientId and Status. Report dropped to under 30 seconds. The client actually mentioned it in a feedback call — not because I told them, but because they noticed. That's the kind of thing that quietly builds trust.</p><p><strong>Second — killing duplicate email reminders in PaymentReminder.</strong> Before my fix, the reminder service occasionally sent the same overdue-invoice email twice to a client. Small bug, but clients were calling in confused and it looked unprofessional. I tracked it down to a race condition when two instances of the service ran simultaneously after a scale-out, fixed it with idempotency tracking in the database, and we had zero duplicate complaints after that. Protecting that client relationship was the actual business outcome.</p><p><strong>Third — the FolioTrack dashboard redesign.</strong> The original spec was a static holdings list. I pushed back and suggested adding real-time NAV calculations and a portfolio composition chart. It took an extra week but that dashboard became the main feature the product owner showed during sales demos. It's hard to quantify but it directly changed how the product was perceived externally.</p><p>None of these are huge revenue numbers I can put on a slide — but they're the kind of wins that people in the business actually noticed and talked about.</p>",
  "followUps": [
    {
      "question": "How do you track the impact of your work day-to-day?",
      "answer": "<p>Honestly I don't do anything formal — no spreadsheet of before/after metrics. But I do make a habit of noting specific numbers when I fix something performance-related: query time before and after, error count in logs before and after a bug fix, deployment time before and after CI/CD improvements. Those numbers end up being useful six months later in appraisals or interviews because I can say 'it went from X to Y' rather than 'I improved it significantly.'</p><p>I also try to look at things from the user's or client's perspective. When the Monday report dropped from 9 minutes to 30 seconds, I knew that mattered because I put myself in the shoes of someone who runs that every week. Technical metrics only mean something when you connect them to someone's actual experience of the product.</p>"
    },
    {
      "question": "Which of these are you most proud of and why?",
      "answer": "<p>Honestly the FolioTrack dashboard one — not because it was the most technically impressive, but because it required me to push back on a spec and justify why extra time was worth it. The index fix was pure technical work. The duplicate email fix was bug chasing. But the dashboard required me to have a product opinion, convince someone else it was worth the effort, and then deliver. That's a different kind of skill and it's one I'm actively trying to build.</p>"
    }
  ],
  "tip": "<strong>Prepare 3 specific stories before any interview</strong> — one technical win, one reliability/quality win, one product/business win. Numbers help but aren't always available. What matters is connecting the work to an outcome someone outside engineering cared about.",
  "tags": ["behavioral", "hr", "achievements", "self-awareness"],
  "sortOrder": 9,
  "isActive": True
},

{
  "id": "beh-010",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "How have you exceeded your KRAs or performance metrics in the last appraisal cycle?",
  "answer": "<p>My formal KRAs are honestly a bit generic — deliver assigned features on time, maintain code quality, participate in code reviews. By those measures I did fine. But what actually got called out in my last appraisal was the stuff that went beyond what I was technically asked to do.</p><p>The biggest one: when our DevOps person left, I picked up setting up proper CI/CD for the CSInvoice project. We were doing manual deployments — literally zipping a build and FTP-ing it to the server. I set up GitHub Actions with build, test, and deploy stages. It wasn't in my KRA, but my manager mentioned it specifically in my review as something that improved the whole team's process, not just my own work.</p><p>The second thing — I started doing more thorough code review comments. Not just approving things with a thumbs-up but actually explaining why something could be done differently, linking to relevant docs. A couple of junior developers on the team told me they found the reviews helpful. My manager mentioned 'technical mentorship' in my appraisal even though I'm not in a formal mentoring role.</p><p>I think the honest answer is: KRAs measure the baseline. What gets you a good appraisal is showing you're thinking about the team and the product, not just your own ticket queue.</p>",
  "followUps": [
    {
      "question": "What would you change about how your performance is currently measured?",
      "answer": "<p>I'd want more emphasis on code quality and technical debt reduction — right now it's easy to look good by closing tickets fast even if you're leaving messy code behind. If there was a metric around 'code review quality' or 'bugs found after your PRs ship' I think it would encourage better habits across the team. It's hard to measure but it matters a lot more long-term than velocity numbers.</p>"
    }
  ],
  "tip": "<strong>Don't just talk about meeting targets — talk about what you did that nobody asked for.</strong> Going beyond the JD is what separates 'meets expectations' from 'exceeds expectations' in most appraisal conversations.",
  "tags": ["behavioral", "hr", "performance", "appraisal", "self-awareness"],
  "sortOrder": 10,
  "isActive": True
},

{
  "id": "beh-011",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "What feedback did you receive in your last performance review, and how did you act on it?",
  "answer": "<p>Two pieces of feedback stood out from my last review.</p><p><strong>First — 'needs to communicate blockers earlier.'</strong> My manager pointed out that a couple of times I'd been stuck on something for a day or two before flagging it, and by then it was affecting the sprint timeline. I was trying to solve problems myself before asking for help — which isn't bad instinct, but the threshold was too high. Since then I've been more deliberate about it: if I've been stuck on something for more than a few hours and I can see the end isn't close, I flag it early. Not as 'I can't do this' but as 'heads up, this is taking longer than estimated, here's why, here's what I'm trying.' It's changed how I communicate during standups.</p><p><strong>Second — 'your technical documentation could be more consistent.'</strong> I'd write detailed comments in complex code but leave straightforward-looking code with no explanation of why a decision was made. I started adding short ADR-style notes in PR descriptions — not just what changed but why. It's made code reviews faster because the reviewer doesn't have to ask why I chose one approach over another.</p><p>I actually appreciate direct feedback, even when it's uncomfortable. It's much more useful than vague praise.</p>",
  "followUps": [
    {
      "question": "How do you handle feedback you disagree with?",
      "answer": "<p>I try to separate my initial reaction from my actual response. Usually when I get feedback I disagree with, my first instinct is defensive — 'but I had a good reason for that.' I've learned to sit with it for a bit before responding. Most of the time, once I'm not reacting emotionally, I can see there's at least a grain of truth in it even if I don't fully agree.</p><p>If after reflection I still think the feedback is off-base, I'll have a genuine conversation about it. 'I hear what you're saying, but here's my perspective — can we talk about where that perception came from?' That's worked better for me than either silently accepting feedback I don't believe or pushing back defensively in the moment.</p>"
    }
  ],
  "tip": "<strong>Always have a specific feedback example ready — not a generic one.</strong> 'I was told to communicate better' is weak. 'I was told to flag blockers earlier, here's specifically what I changed' shows self-awareness and follow-through.",
  "tags": ["behavioral", "hr", "feedback", "self-awareness", "growth"],
  "sortOrder": 11,
  "isActive": True
},

{
  "id": "beh-012",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "very-high",
  "question": "Why do you think now is the right time for a change?",
  "answer": "<p>I've been thinking about this genuinely and the honest answer is two things.</p><p>First, I've been working on the same core codebase for a while now and I'm at the point where I can predict what's going to be hard, what's going to be easy, and roughly how long things will take. That predictability is comfortable, but comfortable isn't where I grow. I want to be in a situation where I'm figuring things out again — new team dynamics, new scale, new architectural challenges. That discomfort is where the real learning happens.</p><p>Second, I've been building towards a more senior-level role — designing systems, not just implementing them. In my current position, the architecture is already defined and most of the interesting decisions were made before I joined. I want to be part of a team where I can contribute to those decisions, not just execute them. I'm not sure that opportunity is available where I am now.</p><p>It's not that anything is broken in my current role — my team is good, the work is decent. But I've been here long enough to know what the ceiling looks like, and I don't think it's where I want to stop.</p>",
  "followUps": [
    {
      "question": "What's the one thing you'll miss most about your current role?",
      "answer": "<p>The team familiarity, honestly. When you've worked with the same people for a while, you develop a shorthand — you know how they review code, what they care about, how they respond under pressure. There's a lot of invisible context that makes collaboration smooth. Starting somewhere new means rebuilding all of that from scratch, which takes time. I'm prepared for that, but it's the part of changing jobs I'm most realistic about.</p>"
    },
    {
      "question": "Have you tried to get these opportunities at your current company?",
      "answer": "<p>Yes, and I think that's important to try first. I've had conversations with my manager about moving into a more senior technical track and about getting involved in architecture discussions earlier. Some of that has happened — I've been included in a few design reviews. But the company structure is such that the senior technical roles are occupied by people who've been there for many years and aren't going anywhere soon. The path exists in theory but the timeline is unclear. I'd rather invest my next few years somewhere where the trajectory is more defined.</p>"
    }
  ],
  "tip": "<strong>Frame it as moving toward something, not away from something.</strong> 'I want more architectural responsibility' lands better than 'I'm stuck.' Even if frustration is part of the truth, what the interviewer needs to hear is what you're excited to go toward.",
  "tags": ["behavioral", "hr", "career-change", "motivation"],
  "sortOrder": 12,
  "isActive": True
},

{
  "id": "beh-013",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "high",
  "question": "Why do you feel you deserve a higher salary?",
  "answer": "<p>I try to approach this factually rather than emotionally, because 'I work hard' isn't really an argument for a higher salary.</p><p>First, market positioning. I've looked at what .NET developers with similar experience and a full-stack profile — .NET backend, Angular, SQL Server, Azure — are making in the current market. What I'm currently earning is below the median for that profile. That gap is my starting point for any salary conversation.</p><p>Second, what I actually deliver. I'm not just writing tickets — I've shipped features end-to-end, fixed production bugs that were affecting client relationships, improved deployment pipelines, and contributed to system design discussions. I own my work in a way that saves the team time and reduces the back-and-forth that junior developers need. That has real value.</p><p>Third, breadth. I'm comfortable across the full stack — I can pick up an Angular bug, an API issue, a database performance problem, or a CI/CD failure and deal with it without needing to hand it off. That kind of versatility means less coordination overhead for the team, which is worth something.</p><p>I'm not expecting a number based on tenure. I'm expecting a number that reflects what I actually bring to a team and what the market says someone with this profile is worth.</p>",
  "followUps": [
    {
      "question": "How did you research the market rate?",
      "answer": "<p>I've looked at a few sources — AmbitionBox, Glassdoor, LinkedIn Salary Insights, and job postings for equivalent roles. Job postings are particularly useful because they tell you what companies are willing to pay for a role right now, not historical data. I've also had honest conversations with peers at other companies — not specific numbers, but ranges. When multiple sources point in the same direction, I feel reasonably confident about the range I'm quoting.</p>"
    },
    {
      "question": "What if we can't match your expected CTC?",
      "answer": "<p>Then I'd want to understand the full picture — not just base salary but what else is on the table. Learning opportunities, the technical complexity of the work, growth trajectory, flexible work arrangements, performance review cycles. If the role is genuinely exciting and the gap isn't large, I'm open to a conversation. But I also have a number below which I won't go regardless of other factors — I've thought about that threshold and I know what it is. I'd rather have an honest conversation about it upfront than either party feel like they compromised in a way they'll regret.</p>"
    }
  ],
  "tip": "<strong>Anchor on market data, not personal need.</strong> 'I need more money' is weak. 'My profile is valued at X in the current market and my current compensation is below that' is a business argument, not an emotional one. Come with data.",
  "tags": ["behavioral", "hr", "salary", "negotiation", "self-awareness"],
  "sortOrder": 13,
  "isActive": True
},

# ─── PROBLEM-SOLVING & OWNERSHIP ───────────────────────────────────────────

{
  "id": "beh-014",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "Have you ever taken ownership of a problem outside your job description? What was the outcome?",
  "answer": "<p>Yeah — the CI/CD thing is the clearest example.</p><p>When our DevOps person left, nobody was officially assigned to maintain the deployment process. At the time we were deploying CSInvoice by manually building locally, zipping the output, and FTP-ing it to the server. It was slow, error-prone — someone once deployed the wrong build because they forgot to switch the connection string. That was a bad day.</p><p>Setting up proper deployment pipelines wasn't in my job description. I was hired as a backend developer. But I'd been wanting to learn GitHub Actions and this was an obvious gap with real consequences, so I took it on. Over a couple of weekends I set up a workflow that builds, runs tests, and deploys to Azure on every push to main. Added environment-specific config management so you can't accidentally deploy dev settings to production.</p><p>The outcome — no more manual deployments, no more wrong-build incidents, and significantly faster release cycles. It also unblocked the team from a process that had been quietly annoying everyone. My manager brought it up in my appraisal as an example of ownership beyond the JD.</p><p>I generally look for these gaps because they're learning opportunities disguised as problems. If something is broken and nobody's fixing it, and you have the skill to fix it, stepping up is usually worth it.</p>",
  "followUps": [
    {
      "question": "How did you decide this was worth your time?",
      "answer": "<p>It was pretty clear this was a recurring problem with compounding costs. Every manual deployment had risk — wrong config, wrong build, someone forgetting a step. And deployments were taking 30+ minutes of someone's time every time. It wasn't a question of 'is this worth it' so much as 'why hasn't someone done this yet.' I had the skill, I had the motivation to learn CI/CD properly, and the pain point was obvious. The decision made itself.</p><p>If it had been a more ambiguous situation — where fixing it wouldn't clearly save time or reduce risk — I'd have been more cautious about spending time on something outside my scope. I try to be pragmatic about where I spend energy that isn't explicitly part of my role.</p>"
    }
  ],
  "tip": "<strong>Ownership means not waiting for permission.</strong> If you see a gap with clear impact and you have the skills, taking it on is what separates engineers who grow fast from those who stay in their lane. Just make sure it's actually a gap and not someone else's territory.",
  "tags": ["behavioral", "hr", "ownership", "initiative", "problem-solving"],
  "sortOrder": 14,
  "isActive": True
},

{
  "id": "beh-015",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "very-high",
  "question": "Tell me about a time you failed and how you handled it.",
  "answer": "<p>There was a deployment on the CSInvoice project where I pushed a migration to production on a Friday afternoon — which, in retrospect, was the first mistake. The migration added a non-nullable column to the Invoices table and I had set a default value, but I'd missed that some stored procedures still tried to insert without specifying that column. Those procs started failing immediately after deployment.</p><p>The failure itself: invoice creation was broken for about 40 minutes before we caught it. It was logged — we had alerts — but it was a Friday at 5:30pm and I wasn't watching the dashboard closely enough after deployment.</p><p>What I did: I rolled back the deployment within about 15 minutes of realizing what happened, fixed the stored procedures, and pushed a hotfix. We communicated to the client that there had been a brief disruption and that it was resolved.</p><p>What I learned — and actually changed about how I work: no schema migrations on Fridays. Period. Also, I now always do a dry-run of migrations in a staging environment that mirrors production as closely as possible, not just in a local dev database. And I stay online and monitoring for at least an hour after any production deployment that includes a database change.</p><p>I'm not proud of the incident but it taught me more about careful deployments than any blog post could have.</p>",
  "followUps": [
    {
      "question": "How did you communicate this failure to your team and manager?",
      "answer": "<p>Directly and immediately — I didn't try to minimize it or frame it as 'there was a brief issue.' I told my manager: 'I deployed a migration that caused production invoice creation to break for 40 minutes. Here's what happened, here's what I did to fix it, here's what I'm changing to make sure it doesn't happen again.' I think owning it clearly is important — both for trust and because it's the only way the team can actually learn from it. If I'd tried to explain it away, the actual lesson would have been lost.</p>"
    }
  ],
  "tip": "<strong>The interviewer is not looking for a story where you come out perfect.</strong> They want to see accountability, learning, and behavioral change. 'I failed, I owned it, I changed something concrete' is the structure. 'It wasn't really my fault' is the answer that kills interviews.",
  "tags": ["behavioral", "hr", "failure", "learning", "accountability"],
  "sortOrder": 15,
  "isActive": True
},

{
  "id": "beh-016",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "How do you prioritize tasks when you're managing multiple deadlines?",
  "answer": "<p>My default framework: urgency vs impact. Not everything urgent is important, and not everything important is urgent. When I have multiple things competing for my attention, I first check which ones are actually blocking someone else — a PR waiting for review, a bug a colleague can't move past without my input. Those go first regardless of what I feel like working on.</p><p>Then I look at what's closest to a delivery date and what the blast radius is if it slips. A feature that impacts a client-facing demo next week gets more priority than an internal refactor, even if the refactor is technically more interesting to work on.</p><p>Practically — when things get genuinely hectic — I write down everything competing for my attention, estimate rough sizes (not Fibonacci, just small/medium/large), and share the list with my manager or team lead. Not to ask them to solve it for me, but to surface the constraint: 'here's what I have, here's what I think the order should be, do you agree or am I missing something?' That conversation often reveals that something I thought was urgent actually isn't.</p><p>In the PaymentReminder project, I had a period where I was simultaneously fixing a production bug, finishing a feature for a sprint, and dealing with a third-party API integration issue. I explicitly wrote down all three with their respective stakes and communicated the priority order to the team. It helped everyone stay aligned on expectations rather than each person wondering why something wasn't done yet.</p>",
  "followUps": [
    {
      "question": "What happens when your manager and a colleague both need something from you at the same time?",
      "answer": "<p>I'm transparent about it. I'll tell both parties what's on my plate and ask which should come first, rather than silently making a call and having someone surprised. Usually the manager has more context about business priorities so they'll often know which is more critical. And most of the time, once both parties know about the conflict, one of them will adjust their expectation voluntarily. The worst thing I can do is silently try to juggle both and deliver both late.</p>"
    }
  ],
  "tip": "<strong>Show your system — not just 'I prioritize by importance.'</strong> Interviewers want to see that you have a consistent method, that you communicate under pressure, and that you don't just disappear into your own queue and hope for the best.",
  "tags": ["behavioral", "hr", "prioritization", "time-management"],
  "sortOrder": 16,
  "isActive": True
},

{
  "id": "beh-017",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "Give an example of a process you improved or optimized in your team.",
  "answer": "<p>The one that had the most visible impact was the deployment process — but let me give a different one since I've mentioned that elsewhere.</p><p>On FolioTrack, our code review process was really inconsistent. Some PRs would get reviewed and merged in a day, others would sit for a week because nobody had time or nobody felt responsible. There was no written expectation about review SLA or what a good review looked like.</p><p>I proposed a few small changes: a PR template that made the author describe what the change does, why it's being done that way, and what they want the reviewer to focus on. And a loose team norm of 'respond to a PR review request within 24 hours, even if just to say you'll look at it by end of week.' We also started doing brief in-person walkthroughs for any PR that touched an architectural boundary — 10 minutes at the whiteboard was often faster than 20 comment threads.</p><p>Within a couple of sprints, the average time from PR open to merge dropped significantly. More importantly, the quality of feedback improved because reviewers had context before they even looked at the diff. It sounds small but it changed the rhythm of how work flowed through the team.</p><p>I didn't have authority to mandate any of this — I just brought it up, explained why I thought it would help, and people were willing to try it.</p>",
  "followUps": [
    {
      "question": "How do you get team buy-in for process changes you want to make?",
      "answer": "<p>I never lead with 'we should do X.' I lead with the problem: 'I've noticed PRs are sitting for 4-5 days and it's making it hard to plan the sprint. Has anyone else felt this?' If others agree there's a problem, proposing a solution feels collaborative rather than like I'm telling people what to do. And I'm always willing to try something for a sprint and evaluate — 'let's try this for two weeks and see if it helps' gets much less resistance than 'from now on we're doing it this way.'</p>"
    }
  ],
  "tip": "<strong>Process improvements don't need a title.</strong> Even without being a team lead, you can propose, pilot, and drive adoption of better ways of working. Show that you notice what's inefficient and do something about it rather than accepting the status quo.",
  "tags": ["behavioral", "hr", "process-improvement", "initiative"],
  "sortOrder": 17,
  "isActive": True
},

# ─── DOMAIN KNOWLEDGE & SKILL APPLICATION ──────────────────────────────────

{
  "id": "beh-018",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "high",
  "question": "What tools, platforms, or technologies do you use daily — and why?",
  "answer": "<p>Day to day it's a pretty consistent set.</p><p><strong>Visual Studio / Rider</strong> for .NET development — VS for the full IDE experience when working on larger projects, Rider when I want faster startup and better refactoring tools. I switch based on what the project needs.</p><p><strong>SQL Server Management Studio</strong> — I'm in there almost daily, either writing queries directly, checking execution plans, or debugging something that doesn't look right from the EF Core side.</p><p><strong>Postman</strong> for API testing during development. I keep Postman collections for every API I work on — it saves a huge amount of time compared to re-typing curl commands or setting up unit tests just to test a single endpoint's behavior.</p><p><strong>Git + GitHub</strong> — PRs, code reviews, GitHub Actions for CI/CD. The workflow is just muscle memory at this point.</p><p><strong>Azure Portal + CLI</strong> — we deploy to Azure App Service so I'm checking deployment logs, app settings, and occasionally scaling settings.</p><p><strong>Chrome DevTools</strong> on the Angular side — network tab for API call debugging, console for JavaScript errors, performance tab when something feels slow on the frontend.</p><p>And honestly — <strong>StackOverflow and GitHub issues</strong> are tools I use daily in the sense that debugging often starts there. I don't pretend I remember every API. Knowing where to look and how to evaluate whether a solution applies to your specific situation is a skill in itself.</p>",
  "followUps": [
    {
      "question": "Is there a tool you recently adopted that changed how you work?",
      "answer": "<p>GitHub Copilot — I was skeptical at first but I've genuinely changed how I use it. I don't use it for generating features wholesale, but for boilerplate-heavy things like writing EF Core migrations, generating test method stubs, or drafting XML doc comments it's a significant time saver. The key is treating it as a first draft you review, not an answer you trust. I've caught it confidently generating wrong code more than once, which is a useful reminder that understanding what it wrote is non-negotiable.</p>"
    }
  ],
  "tip": "<strong>Be specific about why you use each tool</strong> — not just listing them. 'I use Postman because maintaining collections is faster than writing integration tests for exploratory API testing' shows you've thought about it, not just that you know the tool exists.",
  "tags": ["behavioral", "hr", "tools", "tech-stack", "domain-knowledge"],
  "sortOrder": 18,
  "isActive": True
},

{
  "id": "beh-019",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "Can you explain a recent technical concept to a non-technical stakeholder?",
  "answer": "<p>This comes up a lot actually — project managers and product owners ask me to explain things during sprint reviews or planning sessions.</p><p>A recent one: I had to explain why we couldn't just 'turn on' a feature for production users on a Friday evening — specifically why we needed a staging environment test and what database migrations meant.</p><p>The way I explained it: 'Imagine the production database is a filing cabinet that's been set up a specific way for years. The new feature needs to add a new drawer to that cabinet. Before we do that in the real office, we want to practice on an identical cabinet in the back room — make sure the drawer fits, make sure all the existing files still work with the new layout. If we just do it directly in the real cabinet on a Friday, and it turns out the drawer doesn't fit quite right, we have a problem over the weekend with no one around to fix it.'</p><p>They got it immediately. No jargon needed — just a metaphor that maps to something they already understand.</p><p>My general approach: I try to figure out what concept they already understand that's structurally similar to what I'm explaining, and build the bridge from there. Avoid acronyms unless I've already explained what they mean. And I check for understanding — 'does that make sense?' rather than assuming the analogy landed.</p>",
  "followUps": [
    {
      "question": "Have you ever had a stakeholder push back on a technical constraint? How did you handle it?",
      "answer": "<p>Yes — the classic one is 'why can't we just do X quickly?' where X is something that sounds simple from the outside but has real complexity underneath. My approach is to give them a genuine answer rather than just saying no. 'We could do it in a day if we skip the data validation, but here's specifically what could go wrong and here's who would be affected.' I try to give them the option with full information rather than making the decision for them. Most of the time, once they understand the actual risk, they make a sensible call. Occasionally they still want the fast option and then it's my job to document the tradeoff clearly so there's no finger-pointing later.</p>"
    }
  ],
  "tip": "<strong>Analogies beat technical accuracy when the goal is understanding, not precision.</strong> You're not dumbing it down — you're translating. The best engineers can do both: speak precisely with other engineers and accessibly with everyone else.",
  "tags": ["behavioral", "hr", "communication", "stakeholder-management", "domain-knowledge"],
  "sortOrder": 19,
  "isActive": True
},

{
  "id": "beh-020",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "medium",
  "question": "Which domain certifications have you done, and how have they helped your career?",
  "answer": "<p>I haven't done formal certifications yet — that's something I'm being honest about rather than glossing over.</p><p>The reason isn't lack of interest, it's prioritization. For most of the last five years, my learning has been project-driven — I learn what I need to solve the problem I'm working on. That's given me deep practical knowledge in .NET, SQL Server, EF Core, and Angular, but it's not always structured the way certification curricula are.</p><p>I've been planning to take the AZ-204 (Azure Developer Associate) because I've been working with Azure enough that I want to close the gaps I know I have — specifically around Azure Service Bus, Azure Functions, and proper infrastructure-as-code with Bicep. Studying for it systematically is different from learning by doing because it forces you to cover the parts you never happened to need in a project.</p><p>I expect to have that done in the next few months. I'm treating the certification as a forcing function for structured learning, not as the goal itself.</p><p>In the meantime, the unofficial 'certifications' are the things I've shipped — you don't really understand EF Core migrations until you've accidentally broken production with one and fixed it, or understand indexing until you've debugged a slow query in production. That kind of learning doesn't come with a certificate but it tends to be the kind that sticks.</p>",
  "followUps": [
    {
      "question": "Do you think certifications are important for a developer's career?",
      "answer": "<p>They're important for some contexts more than others. For enterprise clients and some large company hiring processes, certifications are a filter — you need them to get through the door. For startups and product companies, they tend to care more about what you've shipped. I think the honest answer is: a certification is evidence that you've systematically studied something to a standard. It's one data point, not the whole picture. I wouldn't hire someone with great certificates and no projects, and I wouldn't dismiss someone with great projects and no certificates. They're different kinds of evidence of the same thing — whether you know what you're doing.</p>"
    }
  ],
  "tip": "<strong>If you don't have certifications, be honest and explain what you're doing instead.</strong> Saying 'I'm working toward AZ-204 because I want to fill specific gaps in my cloud knowledge' is better than either lying or apologizing. Showing a plan is nearly as good as showing a result.",
  "tags": ["behavioral", "hr", "certifications", "learning", "domain-knowledge"],
  "sortOrder": 20,
  "isActive": True
},

{
  "id": "beh-021",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "What trends or changes in your industry are you currently adapting to?",
  "answer": "<p>Three things I'm actively engaging with, not just reading about.</p><p><strong>AI-assisted development.</strong> GitHub Copilot is in my daily workflow now. I've had to learn how to use it well — it's not a replacement for thinking, it's more like having a very fast autocomplete that occasionally suggests the wrong thing with complete confidence. The skill I'm building is knowing when to trust it and when to question it. I think developers who treat it as magic and those who refuse to touch it will both be at a disadvantage.</p><p><strong>.NET cloud-native patterns.</strong> Most of my recent work has been on Azure App Service, but I've been spending time with containerization and .NET Aspire because that's clearly where the ecosystem is heading. Writing code that's infrastructure-aware — proper health checks, graceful shutdown, environment-based config — is increasingly expected even for smaller projects.</p><p><strong>Minimal API vs full MVC.</strong> I've been using full MVC because that's what most of my projects needed, but Minimal APIs are genuinely better for smaller services and I've been experimenting with them in side projects. The mental model shift from controller-heavy design to endpoint-centric design is interesting and I want to be fluent in both.</p><p>I try to have a category of 'things I'm reading about' and 'things I'm actually building with' — and I'm more cautious about claiming expertise in the first category.</p>",
  "followUps": [
    {
      "question": "What trend do you think is overhyped right now?",
      "answer": "<p>Microservices for everything. The pattern has real merit at a certain scale and organizational size, but I've seen it proposed for small teams building internal tools where a well-structured monolith would be simpler, cheaper, and easier to debug. Distributed systems are genuinely harder to operate than people realize when they read about Netflix's architecture. The hidden costs — network latency, distributed tracing, saga patterns for transactions, independent deployment pipelines — add up quickly for teams that don't have the infrastructure maturity to support them. I'm a fan of microservices when the scale and team structure warrant them. I'm skeptical of them as a first-choice default.</p>"
    }
  ],
  "tip": "<strong>Name things you're actually doing, not just aware of.</strong> 'I'm adapting to AI by using Copilot in daily work and learning to evaluate its output critically' is specific. 'AI is changing everything' is not an answer.",
  "tags": ["behavioral", "hr", "trends", "industry", "domain-knowledge"],
  "sortOrder": 21,
  "isActive": True
},

# ─── TEAM COLLABORATION & COMMUNICATION ────────────────────────────────────

{
  "id": "beh-022",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "How do you handle team members who are underperforming?",
  "answer": "<p>This is a sensitive one because 'underperforming' can mean a lot of different things, and I'm not a manager — so I have to be careful about the difference between helping a colleague and overstepping.</p><p>My starting assumption is that underperformance usually has a reason. Someone missing estimates consistently might be struggling with a technology they haven't said they're unfamiliar with, dealing with something personal, or just unclear on what's expected. Assuming laziness or incompetence without checking is almost always wrong.</p><p>In practice — when I've noticed a colleague consistently pushing PRs with the same kinds of issues, or taking much longer than expected on something, I'll have a direct but private conversation. Not 'why is your work slow' but more like 'hey, I noticed you've been stuck on this authentication piece for a few days — is there anything I can help with or any context I can share?' That approach surfaces blockers without putting anyone on the defensive.</p><p>If I can help by pairing on it, I do. If the issue is something that genuinely needs to go to a manager because it's affecting sprint delivery, I'll raise it — but I'd mention to the colleague first that I'm planning to, rather than going behind their back.</p><p>The one thing I won't do is absorb someone else's work silently to protect a deadline. That solves the short-term problem and creates a long-term one.</p>",
  "followUps": [
    {
      "question": "Have you ever had to work closely with someone who consistently blocked progress?",
      "answer": "<p>Once — not underperformance exactly, but someone whose review style was to add large amounts of feedback very late in a PR's life, which meant rework at the worst possible time. I had a direct conversation: 'I've noticed the reviews are coming in late with a lot of changes — is there something about the way I'm writing the PRs that makes them hard to review earlier?' Framing it as my problem to fix rather than their problem to change got a much more open conversation. We ended up agreeing to do quick async walkthroughs before I opened a PR for anything complex, which cut the late feedback significantly. It wasn't about confronting them — it was about changing the system so we both succeeded.</p>"
    }
  ],
  "tip": "<strong>Start with curiosity, not judgment.</strong> Most underperformance has a cause. Ask before assuming. If you're not a manager, your job is to help unblock and escalate only when the team is genuinely at risk — not to manage other people's performance.",
  "tags": ["behavioral", "hr", "teamwork", "underperformance", "communication"],
  "sortOrder": 22,
  "isActive": True
},

{
  "id": "beh-023",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "medium",
  "question": "What's your preferred communication style in a hybrid or remote setup?",
  "answer": "<p>Async-first with clear escalation to sync when it's genuinely faster.</p><p>My default for most things is written communication — Slack message, PR comment, a short document. Written is better for anything that needs to be referenced later, and it forces you to be clearer than you might be in a verbal conversation where you can just hand-wave.</p><p>But I've also learned the hard way that some conversations shouldn't stay async. If I find myself writing a long back-and-forth about a technical decision or a sensitive topic, I'll just ask for a 15-minute call. 'This would be quicker to talk through' is something I say a lot. The right rule isn't 'always async' or 'always meet' — it's matching the medium to the complexity and emotional weight of the conversation.</p><p>A few specific habits I have: I try to be very explicit in async messages about what I need and when I need it — 'can you review this PR, not urgent, before end of week' vs 'blocking my work, need this by EOD.' Ambiguous urgency is genuinely disrespectful of people's attention. I also over-document decisions in tickets and PRs because half the team might not have been in the meeting where the decision was made.</p><p>Remote work requires more intentional communication than in-person. Things that get resolved by bumping into someone in a hallway don't happen automatically — you have to build systems for them.</p>",
  "followUps": [
    {
      "question": "How do you build relationships with teammates you've never met in person?",
      "answer": "<p>It takes longer and it requires deliberate effort. I try to have at least some non-work context with everyone I work closely with — knowing someone has a dog, is into football, is going through a house move — makes the working relationship feel less transactional. I also find that being willing to be occasionally vulnerable or honest about what I don't know builds trust faster than trying to always appear competent. Remote relationships seem to develop faster when people see you as a real person, not just a profile picture on Jira tickets.</p>"
    }
  ],
  "tip": "<strong>Have a clear answer about async vs sync trade-offs</strong> — not just 'I prefer Slack.' Show that you've thought about when each works and when it doesn't. Hiring managers want people who communicate efficiently, not just people who communicate a lot.",
  "tags": ["behavioral", "hr", "communication", "remote-work", "hybrid"],
  "sortOrder": 23,
  "isActive": True
},

{
  "id": "beh-024",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "How do you align cross-functional teams when project objectives are not clear?",
  "answer": "<p>The first thing I try to do is surface the ambiguity explicitly — because sometimes the problem isn't that objectives are unclear, it's that different teams have different assumptions that nobody has compared yet.</p><p>In a project involving FolioTrack, there was a point where the dev team, the product owner, and the QA team all had slightly different ideas of what 'done' meant for a particular feature — the portfolio allocation chart. We were building to one spec, QA was testing against slightly different expectations, and the product owner hadn't clarified because they assumed we'd all read the same document the same way.</p><p>What I did — and I'm not sure I had the authority to do this, but nobody else was doing it — was set up a 30-minute meeting with all three groups and asked everyone to write down on a shared document what they thought the acceptance criteria were. Having it written down in the same place made the divergence obvious immediately. We spent the meeting resolving the differences and came out with explicit, agreed-upon criteria.</p><p>It sounds basic but the issue is usually that nobody wants to be the person who says 'I don't think we all agree on this' because it sounds like they're causing a problem. I've learned to be comfortable being that person, because the cost of catching it early is way lower than the cost of shipping something that doesn't match anyone's expectations.</p>",
  "followUps": [
    {
      "question": "What do you do when you can't get alignment and a decision still needs to be made?",
      "answer": "<p>I escalate with a recommendation, not just a problem. I'll document the two or three options, the pros and cons of each, and my view on which is best given the constraints I'm aware of. Then I bring it to whoever has the authority to decide and give them what they need to make the call quickly. The worst outcome is letting ambiguity sit — it doesn't resolve itself, it just gets more expensive over time.</p>"
    }
  ],
  "tip": "<strong>Ambiguity is a problem you can help solve even without authority.</strong> Surfacing it explicitly, asking the right questions, and documenting agreed answers is something any team member can do. Waiting for a manager to impose clarity is usually slower than facilitating it yourself.",
  "tags": ["behavioral", "hr", "cross-functional", "alignment", "communication"],
  "sortOrder": 24,
  "isActive": True
},

{
  "id": "beh-025",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "How do you ensure your voice is heard in a team of senior professionals?",
  "answer": "<p>I've been in rooms — or calls — where I was clearly the least experienced person and I've learned that being junior doesn't mean being silent. It does mean being more deliberate about how and when you speak.</p><p>A few things that work for me:</p><p><strong>Come prepared.</strong> If there's a design discussion coming up, I spend time beforehand understanding the problem well enough to have an opinion. Walking in without context means I'm reacting rather than contributing. The preparation is what earns the right to speak, not the years of experience.</p><p><strong>Ask good questions.</strong> This is underrated. When a senior developer proposes an approach, asking 'how does this handle the case where X?' or 'what's the trade-off between this and approach Y?' shows you're engaged and thinking. You don't have to have an answer to demonstrate that you're following the conversation seriously.</p><p><strong>Write it down first.</strong> For important discussions, I'll sometimes write out my perspective in a ticket comment or Slack thread before the meeting. It lets me formulate my thinking without the pressure of speaking in real time, and it creates a record. Often someone reads it and raises it in the meeting even if I didn't.</p><p>I've also stopped apologizing before making a point. 'This might be a stupid question but...' is a habit I've been working on breaking. If I've thought about it and it's worth saying, I say it without the pre-apology.</p>",
  "followUps": [
    {
      "question": "Has your idea ever been dismissed early and later turned out to be right?",
      "answer": "<p>Once — and I handled it imperfectly at the time. I'd suggested we add an idempotency key to the PaymentReminder service early on and the senior developer on the project said it was over-engineering for a system that would only ever run on one instance. Six months later when we scaled to two instances and got duplicates, I remembered that conversation. The lesson I took wasn't 'I was right' — it was that I should have been more specific about the risk scenario instead of just asserting the solution. If I'd said 'if we ever add a second instance, this creates a duplicate risk' with a concrete example, it would have been harder to dismiss. The idea was right but the argument wasn't complete enough to be persuasive at the time.</p>"
    }
  ],
  "tip": "<strong>Being heard is earned through preparation, not tenure.</strong> Come with specifics, ask sharp questions, and write down your perspective before meetings. You don't need seniority to contribute — you need to show you've thought about the problem.",
  "tags": ["behavioral", "hr", "communication", "senior-team", "confidence"],
  "sortOrder": 25,
  "isActive": True
},

# ─── LEADERSHIP & INFLUENCE ─────────────────────────────────────────────────

{
  "id": "beh-026",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "Have you ever mentored someone? What was the impact?",
  "answer": "<p>Not formally — I've never had a mentee assigned to me. But informally, yes.</p><p>When a junior developer joined the team about a year ago, I became the person they came to most with questions. Initially it was small things — 'how do I write this LINQ query,' 'what's the difference between AddScoped and AddSingleton.' Over time it became more substantive — talking through whether a design decision made sense, reviewing their PRs more thoroughly than a standard approval, explaining why we structured the data layer a certain way.</p><p>The thing I tried to be deliberate about: not just giving answers but explaining the reasoning. 'The reason we use AddScoped for DbContext is...' instead of just 'use AddScoped.' That took more time per question but it meant they asked fewer questions of the same kind over time, which was better for both of us.</p><p>The impact — hard to measure precisely, but they started writing better PRs. Their questions got more sophisticated. They went from asking 'how do I do X' to asking 'I'm thinking of doing X this way — does that make sense?' which is a meaningful shift. My manager noticed they were ramping up faster than expected and mentioned in a team meeting that the informal mentoring had helped.</p><p>I genuinely enjoy it. Teaching something forces you to understand it better than you did before, which is selfish motivation dressed up as generosity.</p>",
  "followUps": [
    {
      "question": "What's the hardest part about mentoring someone?",
      "answer": "<p>Resisting the urge to just do it for them. When someone's stuck and I can see the answer in two seconds, it's tempting to just fix it. But that doesn't help them. The discipline is asking questions that lead them toward the answer rather than giving it — 'what have you tried so far?' and 'what does the error message actually say?' and 'what do you think is happening?' That process is slower and sometimes frustrating for both parties, but it's the only version that actually transfers the skill.</p>"
    }
  ],
  "tip": "<strong>Informal mentoring counts.</strong> You don't need a formal program to answer. If you've genuinely helped someone grow — explained things to them, reviewed their work carefully, guided their thinking — that's mentoring. Name it and describe the impact.",
  "tags": ["behavioral", "hr", "mentoring", "leadership", "growth"],
  "sortOrder": 26,
  "isActive": True
},

{
  "id": "beh-027",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "high",
  "question": "What do you do when you disagree with your manager's decision?",
  "answer": "<p>The short answer: I say something, once, clearly and with reasons. Then I execute the decision regardless of the outcome of that conversation.</p><p>I had a specific situation where my manager wanted to skip writing integration tests for a new API we were building because of timeline pressure. My view was that the API had enough complexity that without tests we'd be debugging in production six months later, and that cost would be higher than the time saved now.</p><p>I raised it directly: 'I want to flag a concern about this — I think skipping the integration tests on this API creates a specific risk that's worth the extra time to avoid. Can I make the case for keeping them?' He heard me out. His reasoning was that the deadline was non-negotiable and the tests could be added later. I didn't agree, but I understood his constraint.</p><p>What I did next: I wrote the critical-path integration tests — maybe 30% of what I'd have written otherwise — focused on the business rules most likely to break silently. Then I noted in the PR that these were a subset and flagged the gaps explicitly. That way I didn't blow the deadline, but I also didn't just drop the testing entirely.</p><p>Six months later, one of the untested edge cases did cause a production bug. We had the conversation about test coverage again and this time he agreed to allocate time for it. Not because I was trying to be right, but because the evidence was there.</p>",
  "followUps": [
    {
      "question": "Is there a decision you disagreed with but later understood was right?",
      "answer": "<p>Yes — there was a decision to delay a refactor I'd been pushing for on CSInvoice. I thought the codebase in one module was genuinely bad and was slowing us down. My manager wanted to hold off until after the current release cycle. I was frustrated at the time. But in retrospect, he was right — the release had some scope creep and doing a major refactor in the middle of it would have been chaotic. The refactor happened afterward with less pressure and went more smoothly than it would have during a crunch. I was right that the refactor was needed. He was right about the timing. That's a useful distinction — being right about the 'what' and wrong about the 'when.'</p>"
    }
  ],
  "tip": "<strong>'Disagree and commit' is the phrase.</strong> Voice your concern clearly and with reasons — once. Then execute fully. What you must not do: comply silently while signaling to the team you think it's wrong, or half-implement something because you disagree with it. Both are worse than the original decision.",
  "tags": ["behavioral", "hr", "leadership", "disagreement", "manager"],
  "sortOrder": 27,
  "isActive": True
},

{
  "id": "beh-028",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "Tell me about a time you influenced stakeholders without direct authority.",
  "answer": "<p>When I was working on FolioTrack, the product owner had a very specific vision for how the portfolio holdings screen should look — a flat table, sorted by holding size. From a pure usability standpoint, I thought it was hard to scan for the information users actually cared about. I had no authority over product decisions — that was squarely their domain.</p><p>What I did: I spent a few hours building a quick prototype of an alternative layout — a grouped view with portfolio allocation percentages and a simple bar chart — and showed it during a sprint review. I didn't say 'the table is bad.' I said 'I built this to see if it was feasible technically, and I'd love your reaction.' The product owner and two beta users who were in the room immediately said the alternative was clearer.</p><p>The decision shifted not because I argued for it but because I made it easy to evaluate. Showing something is more persuasive than describing it. And I was careful not to make anyone feel like I was criticizing their original idea — I framed it as an experiment, not a critique.</p><p>The new design shipped and became the main thing the product owner showed in demos. I didn't get credit for the design decision — they did, and that's fine. The outcome was what I cared about.</p>",
  "followUps": [
    {
      "question": "What do you do when you genuinely can't persuade someone to make a better decision?",
      "answer": "<p>I document my concern, clearly and without drama. In a ticket comment, a PR description, or a design doc: 'The alternative I proposed is X. We've decided to proceed with Y instead. The risk I see with Y is Z.' That way if Z materializes, the team can learn from it. And if Z never materializes, I learn that my judgment was wrong and update my thinking. Either way, a paper trail of decisions and reasoning is valuable, not as a blame tool but as a learning tool.</p>"
    }
  ],
  "tip": "<strong>Influence is earned through credibility and demonstration, not argument.</strong> Showing > telling. Build the prototype, run the numbers, write the comparison. Make it easy for people to change their minds — don't just give them reasons, give them evidence.",
  "tags": ["behavioral", "hr", "influence", "leadership", "stakeholder"],
  "sortOrder": 28,
  "isActive": True
},

{
  "id": "beh-029",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "Have you led any initiative voluntarily in your current or previous company?",
  "answer": "<p>Two come to mind.</p><p>The CI/CD pipeline I've already mentioned — but a different one: I started a biweekly internal 'tech talk' within our small dev team. Nothing formal — just 30 minutes where someone shares something they've learned or been working on. I started it because I noticed we were all working in fairly isolated tracks and not cross-pollinating knowledge. I'd learn something useful about EF Core performance and it would stay in my head; a teammate would figure out a neat Angular pattern and nobody else would know about it.</p><p>I kicked it off by volunteering to do the first one — on index fragmentation and the execution plan improvements I'd made on CSInvoice. Three other people came, which at first felt like low turnout, but after two or three sessions it became a standing thing people actually looked forward to. Over about four months we covered topics ranging from SQL query tuning to Angular reactive forms to how to set up a staging environment in Azure.</p><p>It didn't require any budget or approval. It just required someone to say 'let's do this' and do the first one to show it was worth showing up for. The actual knowledge sharing was the outcome, but the side effect was a tighter, more collaborative team culture.</p>",
  "followUps": [
    {
      "question": "What would you do if the initiative you started didn't get traction?",
      "answer": "<p>I'd have an honest conversation about it rather than letting it quietly die. Either it's not the right format (maybe async written knowledge sharing works better for this team than synchronous talks), or the timing is wrong, or people don't see the value yet. Understanding which is more useful than just trying harder at the same thing. I'd be willing to pivot the format or scope it down — maybe one person doing a quick 10-minute walkthrough of something interesting per sprint retro rather than a separate session. The goal is the knowledge sharing, not the specific format I happened to start with.</p>"
    }
  ],
  "tip": "<strong>Voluntary initiatives don't need a stage — they just need a first step.</strong> Starting small, doing it yourself first, and making it low-effort for others to join is how most organic initiatives get traction. Title or seniority aren't prerequisites.",
  "tags": ["behavioral", "hr", "leadership", "initiative", "culture"],
  "sortOrder": 29,
  "isActive": True
},

{
  "id": "beh-030",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "How do you make your presence felt in leadership meetings?",
  "answer": "<p>I've been in a handful of technical design and planning meetings where I was definitely the most junior person in the room, and I've had to figure out how to contribute without either staying silent the whole time or overcompensating by talking too much.</p><p>What I've found works: come with one specific, well-thought-out point rather than trying to weigh in on everything. If I've prepared for the meeting, I usually have one angle that hasn't been covered yet — a risk, a dependency, a user scenario that the architecture doesn't account for. One sharp observation contributes more than five generic comments.</p><p>I also find that asking a well-timed question is often more valuable than making a statement. 'What happens if [specific scenario]?' or 'Have we considered [edge case]?' surfaces something worth discussing without requiring me to have the answer myself. Good questions show you're thinking at the right level.</p><p>Outside the meeting, I try to be helpful in concrete ways — volunteering to write up the decision summary, following up on action items I said I'd do, sharing a relevant resource afterward. That builds a reputation over time of being someone who contributes reliably, which means people are more likely to listen when I do speak.</p><p>I'll be honest: I don't always get this right. There are meetings where I stayed too quiet and later kicked myself for not saying something. It's a skill I'm still developing.</p>",
  "followUps": [
    {
      "question": "How do you handle it when someone talks over you or takes credit for your idea?",
      "answer": "<p>In the moment, I'll often try to reconnect to my point after the interruption — 'going back to what I was saying...' calmly, not aggressively. If someone presents an idea I'd already raised as if it's new, I'll link it: 'Yes, that connects to the point I mentioned earlier about X.' Politely, not pointedly. For persistent patterns, I'd have a private conversation. I don't think public confrontation helps — it creates defensiveness, not change. And I try to check if I'm doing something that makes it easy to interrupt or dismiss — speaking too quietly, not finishing my sentences, using too many hedges before getting to the point.</p>"
    }
  ],
  "tip": "<strong>Presence comes from quality of contribution, not quantity.</strong> One specific, well-prepared point beats five vague ones. Ask good questions. Volunteer for follow-through. Reputation builds slowly and through consistency — not through trying to dominate any one meeting.",
  "tags": ["behavioral", "hr", "leadership", "meetings", "presence"],
  "sortOrder": 30,
  "isActive": True
},

# ─── BUSINESS IMPACT & NUMBERS ──────────────────────────────────────────────

{
  "id": "beh-031",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "high",
  "question": "How did your work contribute to company revenue, cost-saving, or client retention?",
  "answer": "<p>I'll be honest — I'm not always close enough to the commercial side to quote exact revenue numbers, but I can connect my work to outcomes that had commercial relevance.</p><p><strong>Client retention:</strong> The duplicate email bug in PaymentReminder was causing clients to complain and question the reliability of the product. Fixing that directly preserved a client relationship that had started to show friction. The account manager mentioned after the fix that one client who'd been making noises about evaluating alternatives went quiet.</p><p><strong>Cost saving:</strong> The CI/CD pipeline I set up eliminated a manual deployment process that was costing about 30–45 minutes of developer time per release, across maybe 2 releases per week. Over a year that's probably 50+ hours of developer time saved — at developer billing rates, not insignificant. More importantly, it eliminated the risk of deployment errors that had previously caused rollbacks and emergency fixes.</p><p><strong>Revenue-adjacent:</strong> The FolioTrack dashboard changes made the product significantly more demo-able, which the sales team used in new client presentations. I can't attribute revenue to it directly, but I know it was a specific feature highlighted in at least two successful demos.</p><p>I try to think in these terms when I'm doing technical work — not every PR has business impact, but the ones that do are worth being clear-eyed about. It changes how I prioritize work and how I communicate it.</p>",
  "followUps": [
    {
      "question": "How do you decide what technical work is worth doing given business constraints?",
      "answer": "<p>I try to frame technical work in terms of risk and cost. A refactor isn't worth doing just because the code is messy — it's worth doing when the mess is slowing down feature delivery or causing bugs. A performance optimization isn't worth doing just because it's satisfying — it's worth doing when real users are experiencing real slowness. Connecting technical health to business outcomes is the only argument that consistently gets buy-in from non-technical stakeholders, and it's also just a more honest way to think about prioritization.</p>"
    }
  ],
  "tip": "<strong>Even without revenue access, you can connect your work to business outcomes.</strong> Client retention, time saved, risk eliminated, product quality improved — these are all business contributions. Think about the downstream effect of what you built and be ready to articulate it.",
  "tags": ["behavioral", "hr", "business-impact", "revenue", "client-retention"],
  "sortOrder": 31,
  "isActive": True
},

{
  "id": "beh-032",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "Can you quantify your results in the last project you led or contributed to?",
  "answer": "<p>For CSInvoice, the numbers I can give with confidence:</p><ul><li>Invoice creation report time reduced from ~8 minutes to under 30 seconds after index optimization — that's a 94% reduction in a report the finance team ran weekly.</li><li>Deployment time from merge to production dropped from roughly 45 minutes of manual work to under 10 minutes of automated CI/CD pipeline, with near-zero error rate vs occasional human errors before.</li><li>After fixing the duplicate reminder bug in PaymentReminder: zero duplicate complaint incidents in the 4+ months since, compared to roughly 2–3 incidents per month before the fix.</li></ul><p>For FolioTrack:</p><ul><li>The real-time portfolio dashboard shipped in about 3 weeks of development, including the Angular visualization layer I hadn't worked with before. The product owner had estimated 5 weeks for a simpler version — we delivered more in less time partly because of early design decisions about the data model that saved us rework.</li></ul><p>I'll admit some of these numbers are approximations from memory and logs rather than a formal measurement system. I'm more careful now about noting before-and-after metrics at the time of a change rather than trying to reconstruct them later.</p>",
  "followUps": [
    {
      "question": "What would you do differently to better track and communicate your impact?",
      "answer": "<p>Keep a running personal 'impact log' — a simple document where I note the before/after on any change that has a measurable outcome. Query time before and after a fix, error count before and after a bug fix, time saved by a new process. Even rough numbers captured at the time are better than trying to recall them six months later in an appraisal or interview. It takes maybe five minutes when you do it right after a change, and it's essentially free data collection.</p>"
    }
  ],
  "tip": "<strong>Numbers don't have to be exact to be credible.</strong> 'Report time dropped from ~8 minutes to under 30 seconds' is useful even as an estimate. What undermines credibility is vague language like 'significantly improved' without any anchor. Even approximate before/after is better than nothing.",
  "tags": ["behavioral", "hr", "results", "metrics", "business-impact"],
  "sortOrder": 32,
  "isActive": True
},

{
  "id": "beh-033",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "Have you contributed to any key business transformation?",
  "answer": "<p>The CI/CD and automation work I did is the closest I'd come to calling 'transformational' at the scale I've worked in.</p><p>Before I joined, the CSInvoice team had a development process that was entirely manual — code review in person, deployment by hand, no automated testing in the pipeline. Not because people didn't know better, but because no one had prioritized building the infrastructure. By the time I left that project, we had GitHub Actions running on every push, automated builds, and a staging environment that mirrored production for QA.</p><p>That's not a business transformation in the sense of 'we pivoted our entire product strategy.' But it meaningfully changed how the team operated — faster release cycles, fewer deployment-related bugs, lower stress around releases. The team could ship more confidently, which meant the business could respond to client requests and market changes faster.</p><p>I think for someone at my stage of career, 'transformation' usually means changing how your immediate team or project works in a lasting way. I haven't been part of a company-wide digital transformation initiative, and I wouldn't claim otherwise. But the changes I've contributed to in smaller scope have been durable ones.</p>",
  "followUps": [
    {
      "question": "What kind of transformation would you want to contribute to in your next role?",
      "answer": "<p>I'd like to work on something that's genuinely scaling — a product that's moving from hundreds of users to thousands, or from monolithic architecture to something more distributed. That transition is where a lot of interesting technical decisions happen that I want to be part of. Specifically, I want experience with the architectural conversations that happen when scale forces you to change the system, not just extend it. That's a kind of transformation that requires both technical and business thinking, and it's where I want to grow.</p>"
    }
  ],
  "tip": "<strong>Scale your answer to your actual experience.</strong> Not everyone has been part of a company-wide transformation. Describing how you changed how a team or project works is legitimate and honest. Inflating it sounds hollow; being specific sounds credible.",
  "tags": ["behavioral", "hr", "transformation", "business-impact", "leadership"],
  "sortOrder": 33,
  "isActive": True
},

{
  "id": "beh-034",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "What business KPIs do you track in your current role?",
  "answer": "<p>I track a mix of technical and business-adjacent metrics, depending on what I'm working on.</p><p>On the technical side: application error rate (from logs / App Insights), API response times on key endpoints, deployment frequency, and time to fix production bugs. These are things I can influence directly and that correlate to product quality.</p><p>For the specific projects I work on: in PaymentReminder I tracked the number of duplicate email incidents (which was my main success metric after fixing the bug). In CSInvoice I paid attention to the report run times and the number of rollbacks after deployments.</p><p>Business-side KPIs I have visibility into but less direct influence over: client-reported issues per sprint, feature delivery vs sprint commitment rate, and occasionally the client NPS scores that come through after major releases.</p><p>I'll be honest that I'm not always close to the commercial KPIs like revenue, churn, or contract renewals — that sits with the account management and sales side. But I think it's worth a developer understanding at least one level up from the code: what does success look like for the product, and how does my work connect to it? That question makes for better prioritization decisions.</p>",
  "followUps": [
    {
      "question": "Have you ever changed what you were building because of a KPI trend?",
      "answer": "<p>Yes — after tracking API response times we noticed one endpoint used by the mobile team was getting consistently slow as data grew. I flagged it to the product owner before it became a user complaint. We prioritized a query optimization in the next sprint rather than waiting for users to notice. The KPI trend gave us the heads-up that made it a proactive fix rather than a reactive one. That's the practical value of actually watching metrics rather than just setting up dashboards and ignoring them.</p>"
    }
  ],
  "tip": "<strong>Connect your technical metrics to business outcomes.</strong> 'I track error rate' is weak. 'I track error rate because it correlates directly to client support tickets, and reducing it means less time spent on reactive fixes' shows you understand why the metric matters.",
  "tags": ["behavioral", "hr", "kpi", "metrics", "business-impact"],
  "sortOrder": 34,
  "isActive": True
},

{
  "id": "beh-035",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "How do you measure success in your work?",
  "answer": "<p>At multiple levels, honestly.</p><p><strong>Short-term:</strong> Did it work as intended? No obvious bugs, the feature behaves as specified, the tests pass, the code review didn't surface major issues. That's the baseline — you can't claim success if the basic quality bar isn't met.</p><p><strong>Medium-term:</strong> Did it hold up after it shipped? Did production surface edge cases we didn't catch? Did the feature require a lot of hotfixes? A feature that ships cleanly and stays clean is more successful than one that ships and then generates two weeks of bug tickets.</p><p><strong>Long-term:</strong> Does someone in the business care that it exists? Did the finance team notice the report got faster? Did a client mention the new dashboard feature unprompted? Those moments — when something you built surfaces in a non-technical conversation as something that matters — are the clearest signal that the work had actual impact.</p><p>There's also a developer-facing measure I care about: could someone else maintain this code a year from now without needing me to explain it? If the answer is no, I haven't fully succeeded even if the feature works. Code has a longer life than any single developer's time on a project.</p>",
  "followUps": [
    {
      "question": "How do you handle it when you worked hard on something but it gets cut or doesn't land well?",
      "answer": "<p>It's disappointing — that's honest. But I try to separate the quality of the work from the outcome of the decision to cut it. A feature can be well-built and still be cut for business reasons that are completely valid. What matters is that I understand why it got cut, learn from it if there's something to learn about misjudging requirements or over-engineering, and move on without carrying resentment about it. The sunk cost of the work is done — the question is what to do next.</p>"
    }
  ],
  "tip": "<strong>Define success at multiple time horizons.</strong> Short-term (does it work), medium-term (does it hold up), long-term (does it matter). The most impressive answer shows you think beyond your own ticket queue.",
  "tags": ["behavioral", "hr", "success", "quality", "impact"],
  "sortOrder": 35,
  "isActive": True
},

# ─── SALARY, GROWTH & EXPECTATIONS ─────────────────────────────────────────

{
  "id": "beh-036",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "very-high",
  "question": "What's your current CTC and what are your salary expectations — and why?",
  "answer": "<p>I'll be transparent on this — I think dancing around numbers is a waste of both parties' time.</p><p>My current CTC is [your current figure]. Based on the market research I've done — looking at AmbitionBox, LinkedIn Salary Insights, and a few job postings for equivalent roles — a .NET full-stack developer with 5 years of experience, working across .NET 8, Angular, SQL Server, and Azure, is typically positioned in the range of [market range]. My target is [your expectation], which sits within that range and reflects the specific combination of backend depth and frontend capability I bring.</p><p>The reason I'm not anchoring lower: I've done enough in my current role to understand what I deliver, and I'm not looking to undervalue myself to get a faster offer. But I'm also not naming a number and refusing to discuss it — I'm genuinely interested in this role and there's room for a conversation if the package structure includes things like performance bonuses, stock, learning budget, or flexibility that affect the overall value.</p><p>What I want to avoid is spending three interview rounds finding out there's a 30% gap on compensation. So if the range I've described doesn't work for this role, I'd rather know now than at the offer stage.</p>",
  "followUps": [
    {
      "question": "Are you willing to negotiate?",
      "answer": "<p>Yes — but with parameters. I have a bottom line below which I won't go, and I've thought about what that is. Above that threshold I'm flexible, especially if there are non-cash components that genuinely matter to me — clear growth path, interesting technical work, flexibility on remote vs in-office, learning budget. What I won't do is agree to something I'm not satisfied with because I'm uncomfortable with the negotiation. That starts the relationship on the wrong foot for both sides.</p>"
    }
  ],
  "tip": "<strong>Name your number — don't make them drag it out of you.</strong> Vague answers ('I'm flexible') signal you don't know your value or you're afraid to commit. Do the market research, come with a range, and explain why. Confidence in salary conversations is a proxy for confidence in general.",
  "tags": ["behavioral", "hr", "salary", "negotiation", "expectations"],
  "sortOrder": 36,
  "isActive": True
},

{
  "id": "beh-037",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "Why do you think you're underpaid currently?",
  "answer": "<p>I want to be careful how I answer this because it could sound like complaining, and I'm not trying to do that.</p><p>When I joined my current role, the compensation was fair for my experience level at the time. The problem is that over five years my skills, output, and scope of contribution have grown significantly — but salary increments in my company have been largely inflation-based. The gap between what I do today and what I was hired to do is substantial, but the compensation adjustment hasn't kept pace with that growth.</p><p>More concretely: when I look at the market for someone with my current skillset — full-stack .NET, production deployments to Azure, SQL Server performance work, Angular — the number is notably higher than what I'm earning. It's not that I was always underpaid; it's that the market has moved, my skills have grown, and those two factors together have created a gap.</p><p>I've had the salary conversation with my manager. The company's position is that their increment structure is fixed and they can't make exceptions even for market-rate adjustments. I respect that as a policy, but it means the only way to close the gap is to change companies. That's a rational decision, not an emotional one.</p>",
  "followUps": [
    {
      "question": "If your current company matched the market rate tomorrow, would you still leave?",
      "answer": "<p>Honestly — probably still yes, but for different reasons. The salary gap accelerated the decision, but the deeper motivation is the growth ceiling I mentioned. Even at market rate, the path to more senior technical contributions isn't clear at my current company. I want to work on larger-scale systems, be involved earlier in architectural decisions, and grow toward a tech lead or senior developer role in a way that has defined milestones. That opportunity isn't compensation-dependent — it's structural. The salary question and the growth question both point to the same answer, just for different reasons.</p>"
    }
  ],
  "tip": "<strong>Frame underpayment as a structural issue, not a resentment story.</strong> 'My growth exceeded increments over 5 years' is a business argument. 'My company doesn't value me' is an emotion. Same situation, very different impression.",
  "tags": ["behavioral", "hr", "salary", "underpaid", "career-change"],
  "sortOrder": 37,
  "isActive": True
},

{
  "id": "beh-038",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "high",
  "question": "If offered a counteroffer by your current employer, what would you do?",
  "answer": "<p>I've thought about this because it's a real scenario and I wanted to have a clear answer for myself before I was in the room.</p><p>My honest answer: it depends on what's in the counteroffer, but my default is to decline.</p><p>Here's why. The moment you put in your notice, something changes about how you're perceived at the company. You've signaled that you were willing to leave. Even if they match the number, the reason you were looking in the first place hasn't gone away — it's just been temporarily addressed. And there's often an unwritten clock that starts ticking: 'we retained them for now, but let's plan accordingly.' The statistics on how long people who accept counteroffers actually stay are not encouraging.</p><p>The exception would be if the counteroffer addressed the non-compensation reasons I was leaving — if they said 'we hear you on the growth path, here's a new role with more scope and a defined timeline to senior developer.' That would make me think seriously. But a number match alone wouldn't be enough.</p><p>I'd also be transparent with you: if I'm at the stage of interviewing seriously, it means I've already given this significant thought. A counteroffer at offer stage isn't going to change a decision I've been working toward for months.</p>",
  "followUps": [
    {
      "question": "Have you already told your current employer you're looking?",
      "answer": "<p>No — and I wouldn't until I have a concrete offer in hand. That's not deception, it's prudence. Signaling that you're looking before you have a destination creates uncertainty without benefit. I'll handle the resignation conversation professionally and with appropriate notice, but not before I'm ready to commit to the move.</p>"
    }
  ],
  "tip": "<strong>Have a clear position on counteroffers before you're asked.</strong> Interviewers ask this to gauge how serious you are and whether you're just using their offer as leverage. A thoughtful, honest answer ('I'd consider it only if it addressed the non-compensation reasons I'm leaving') is more credible than 'I definitely won't accept it' or a vague 'it depends.'",
  "tags": ["behavioral", "hr", "counteroffer", "salary", "career-change"],
  "sortOrder": 38,
  "isActive": True
},

{
  "id": "beh-039",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "high",
  "question": "What kind of hike are you expecting — and how do you justify it?",
  "answer": "<p>I'm targeting a hike in the range of 30–40% over my current CTC, and I want to explain how I got to that number rather than just asserting it.</p><p>First, market positioning. The range for a .NET developer with my experience level and stack — five years, full-stack, cloud-deployed production systems — is meaningfully higher than what I'm currently earning. Even a 30% increase would put me at the lower end of that market range, not above it.</p><p>Second, what's changing in this move. When you change companies you take on risk — new team, new codebase, new processes, a ramp-up period where you're not at full contribution. The market generally compensates for that transition risk with above-inflation increments. A lateral move in compensation doesn't make sense given that.</p><p>Third, what I bring. I'm not walking in as a blank slate — I have production experience with the specific stack you're hiring for, I've shipped features end-to-end, I've dealt with real production bugs. The ramp-up time for someone like me is shorter than for someone you'd bring in fresh from a generic background. That has value that should be reflected in the offer.</p><p>I'll also say: I'm not fixed on 30-40% as an absolute line if the overall package — role scope, learning opportunity, team quality — is compelling. But that's the range I'm starting from and I've done my homework on why.</p>",
  "followUps": [
    {
      "question": "What if we can only offer 20%?",
      "answer": "<p>Then I'd want to understand what else is on the table. Variable pay, performance review frequency, specific technical work I'd be doing, career track clarity. If the role is genuinely differentiated in those dimensions and the 20% puts me at market for what I'm doing, I could consider it seriously. But if it's 20% plus a generic 'we'll see how it goes' on growth — that's probably not enough to make the transition make sense. I'd rather have an honest conversation about it than either side feel pressured into a deal that doesn't work.</p>"
    }
  ],
  "tip": "<strong>Justify your expected hike with data, not desire.</strong> Market range + transition risk + your specific value = a business argument. Just saying 'I need 40%' without reasoning sounds like a wish. Same number with reasoning sounds like a negotiation.",
  "tags": ["behavioral", "hr", "salary", "hike", "negotiation"],
  "sortOrder": 39,
  "isActive": True
},

{
  "id": "beh-040",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "Why do you think you haven't been shortlisted by top companies earlier?",
  "answer": "<p>That's a pointed question and I want to answer it honestly rather than defensively.</p><p>Looking back, I think there have been a few real factors.</p><p><strong>Resume gaps:</strong> For most of my career I've been heads-down building projects and not focused enough on how to present what I've built. My previous resume listed technologies and responsibilities, not outcomes and impact. That's a packaging problem, not a capability problem, but it matters in a competitive shortlist.</p><p><strong>DSA preparation:</strong> Top-tier product companies filter heavily on algorithmic problem-solving, and I hadn't been practicing that systematically. I write production code that solves business problems — I hadn't been maintaining the kind of coding fluency that leetcode-style interviews test. That's been a deliberate gap I'm closing.</p><p><strong>Interview preparation generally:</strong> Behavioral questions, system design, explaining my projects clearly and confidently — these are skills in themselves, separate from technical ability. I was underestimating how much preparation they require. The work I'm doing now on both the technical and behavioral side is much more intentional than what I was doing a year ago.</p><p>I don't think the underlying capability was the blocker. But capability that isn't legible in an interview process doesn't count. I'm working on that translation layer.</p>",
  "followUps": [
    {
      "question": "What specifically are you doing differently now?",
      "answer": "<p>Structured practice — daily coding problems to rebuild algorithmic fluency, system design sessions using mock interview formats, and explicitly preparing stories for behavioral questions using STAR rather than winging it. I've also gotten much more specific about targeting roles that match my actual profile rather than spray-applying. The quality of preparation is much higher now than before.</p>"
    }
  ],
  "tip": "<strong>Answer honestly without self-pity or defensiveness.</strong> Attributing past misses to bad luck or unfair processes is a red flag. Attributing them to specific, correctable gaps — and naming what you've done about them — signals maturity and self-awareness.",
  "tags": ["behavioral", "hr", "self-awareness", "career", "shortlisting"],
  "sortOrder": 40,
  "isActive": True
},

# ─── CULTURE FIT & LONG-TERM VISION ─────────────────────────────────────────

{
  "id": "beh-041",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "medium",
  "question": "What type of work environment helps you thrive?",
  "answer": "<p>A few things matter a lot to me, and I've learned them from noticing the difference when they're present vs absent.</p><p><strong>Trust over surveillance.</strong> I do my best work when I'm given a problem and trusted to figure out how to solve it — with check-ins and collaboration, but not micromanagement of the how. The best environments I've been in have clear expectations about outcomes and flexibility about how you get there.</p><p><strong>Code quality taken seriously.</strong> I've worked in environments where code reviews were a formality and tech debt was never discussed, and environments where there was genuine care about how things were built. The second kind is better — not because of perfectionism, but because it makes the work feel meaningful and the codebase actually get better over time.</p><p><strong>People who are better than me in at least some dimension.</strong> I learn the most from working with people I can learn from. Not necessarily senior by title — sometimes it's a peer who approaches a problem differently and I pick up the pattern. An environment where everyone's at the same level is comfortable but not growth-inducing.</p><p><strong>Psychological safety to say 'I don't know.'</strong> Some teams treat not knowing something as a weakness to hide. The best teams treat it as a starting point for figuring it out together. I'm much more effective in the second kind.</p>",
  "followUps": [
    {
      "question": "What kind of environment do you struggle in?",
      "answer": "<p>High bureaucracy and slow decision-making — where getting something as simple as a library upgrade requires three approval layers and two weeks. I understand that process and governance exist for good reasons, especially in regulated industries. But when the overhead of process starts to outweigh the actual work, it's hard to stay motivated. I need to feel like what I'm doing actually moves something forward, not just satisfies a checklist.</p>"
    }
  ],
  "tip": "<strong>Be honest about what you actually need, not what sounds good.</strong> 'I thrive anywhere with a good team' is non-information. Specific answers like 'I need environments where technical quality is taken seriously' help both you and the interviewer figure out if this is actually a good fit.",
  "tags": ["behavioral", "hr", "culture", "environment", "work-style"],
  "sortOrder": 41,
  "isActive": True
},

{
  "id": "beh-042",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "How do you handle criticism or feedback?",
  "answer": "<p>My honest answer: it depends on the quality of the feedback and whether I'm in a good headspace that day — which is a more honest answer than 'I always welcome feedback with open arms.'</p><p>What I've gotten better at: separating the feedback from the delivery. If someone gives me harsh feedback in a way that feels personal, I try to extract the technical or behavioral content and engage with that rather than getting caught up in the tone. 'The PR has a design issue' and 'this PR is badly designed' are the same information delivered differently. Getting defensive about the delivery means I miss the content.</p><p>Something that helps me: I try to treat code review feedback as being about the code, not about me. I wrote that code, but I'm not the code. That distance makes it easier to hear 'this approach has a performance issue' as useful information rather than as criticism of me as a developer.</p><p>The harder kind of feedback is behavioral — 'you're not communicating enough' or 'you seem disengaged in meetings.' That's harder to separate from identity. My strategy there is to get specific: 'what would look different to you if I were doing this better?' Vague feedback is hard to act on; concrete behavior change is achievable.</p><p>And I try to give feedback the same benefit of the doubt I'd want. If my manager says something that stings, I assume they're trying to help me rather than to be difficult. That assumption is usually right.</p>",
  "followUps": [
    {
      "question": "Give an example of feedback that changed how you work.",
      "answer": "<p>The 'communicate blockers earlier' feedback from my last review. I genuinely hadn't realized I was doing it — I thought I was being self-sufficient by trying to solve problems myself first. The feedback reframed it for me: it's not about capability, it's about shared visibility. When I'm stuck and not flagging it, other people are planning around an assumption that I'm making progress. Changing that behavior — flagging blockers earlier with context — changed how reliably people could plan around my work. That was worth more than the discomfort of saying 'I'm stuck' sooner.</p>"
    }
  ],
  "tip": "<strong>Show you've actually changed something based on feedback.</strong> Saying 'I'm open to feedback' is easy. 'Here's specific feedback I received and here's concretely what I changed as a result' is the answer that earns trust.",
  "tags": ["behavioral", "hr", "feedback", "criticism", "self-awareness"],
  "sortOrder": 42,
  "isActive": True
},

{
  "id": "beh-043",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "How do you ensure continuous learning?",
  "answer": "<p>I have a few practices that I've found actually stick vs ones that sound good but don't.</p><p><strong>Project-driven learning.</strong> The most effective learning I've done has been trying to solve a real problem I was stuck on. I learned EF Core performance by debugging a slow query in production. I learned GitHub Actions by setting up CI/CD for a real project. Theoretical learning without a problem to apply it to evaporates quickly for me.</p><p><strong>One thing at a time.</strong> I've tried keeping 5-item learning lists and I'm never consistent with them. Now I pick one thing to go deep on for a period — right now it's system design. I read about it, I try to apply the patterns in side projects, I think about how the systems I currently work on compare to what I'm learning. Depth beats breadth for actually retaining something.</p><p><strong>Following specific people.</strong> Not newsletters, not generic 'top 10 things' articles. Specific practitioners who write deeply about things I care about — Nick Chapsas for .NET patterns, Martin Fowler for architecture, specific GitHub repositories of tools I use. That content is signal-heavy vs noise-heavy.</p><p><strong>Teaching what I learn.</strong> Even small things — explaining something in a PR comment, doing a mini knowledge-share with a colleague. The act of explaining forces gaps in your understanding to the surface. If I can't explain it simply, I don't understand it well enough.</p>",
  "followUps": [
    {
      "question": "What are you learning right now?",
      "answer": "<p>System design, specifically. I've been working through distributed systems concepts — consistent hashing, consensus algorithms, how large-scale systems handle data replication and failure. I'm using a combination of reading (DDIA is on my desk) and applying the ideas conceptually to systems I already understand. I'm also experimenting with .NET Aspire for local orchestration of multi-service setups, because I want to understand what modern cloud-native .NET development looks like before I'm in a situation where I have to learn it under pressure.</p>"
    }
  ],
  "tip": "<strong>Name specific resources and specific topics.</strong> 'I read tech blogs and watch YouTube' is forgettable. 'I'm currently going through DDIA and applying the concepts to how I'd design the notification system I worked on last year' is specific and shows genuine engagement.",
  "tags": ["behavioral", "hr", "learning", "growth", "self-improvement"],
  "sortOrder": 43,
  "isActive": True
},

{
  "id": "beh-044",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "medium",
  "question": "What kind of projects excite you the most?",
  "answer": "<p>The honest answer has a few dimensions.</p><p><strong>Projects with real users and real feedback.</strong> Internal tools can be interesting, but there's something qualitatively different about building something that has a human on the other end who's either pleased or frustrated by what you made. The FolioTrack dashboard was exciting partly because the product owner brought beta users into reviews — seeing someone interact with something you built and respond to it in real time is motivating in a way that internal tooling rarely is.</p><p><strong>Projects where the domain is genuinely complex.</strong> The invoice management work was interesting not because the technology was cutting-edge but because the business logic was surprisingly nuanced — rounding rules, multi-currency handling, edge cases in how invoices get amended. Getting that right required really understanding the domain, not just implementing a spec. I find that kind of problem more engaging than technically flashy work that's shallow underneath.</p><p><strong>Projects with some performance dimension.</strong> Query optimization, reducing API latency, improving load times — I find these genuinely enjoyable in a way that's hard to explain. There's something satisfying about having a before/after number that's unambiguous. The work either made it faster or it didn't.</p><p>What doesn't excite me as much: pure maintenance work with no design space, or highly specced work where I'm just implementing someone else's detailed solution and there's no room to think about whether the solution is right.</p>",
  "followUps": [
    {
      "question": "What's a project you'd build from scratch if you could?",
      "answer": "<p>A developer-focused personal finance tracker — something that understands income patterns that are irregular (freelance, bonuses, salary changes) and helps model forward projections. I'd build it event-sourced because financial data is inherently append-only and having a full audit trail matters. .NET 8 API, Angular frontend, SQLite for the local-first version. The reason this excites me: financial domain logic is surprisingly hard to get right (rounding, currency, time-series projections), and I've already built half the building blocks in the invoice and portfolio work. It's the kind of project where the domain knowledge I already have translates directly into something I'd actually use.</p>"
    }
  ],
  "tip": "<strong>Be specific about what genuinely interests you — not what sounds impressive.</strong> Interviewers can tell the difference between authentic enthusiasm and performed enthusiasm. Name actual projects, actual domains, actual technical challenges that you've found engaging.",
  "tags": ["behavioral", "hr", "motivation", "interests", "culture-fit"],
  "sortOrder": 44,
  "isActive": True
},

# ─── SITUATIONAL & REAL-WORLD SIMULATION ────────────────────────────────────

{
  "id": "beh-045",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "What would you do if you had no support from your team but still had to deliver?",
  "answer": "<p>This has happened — not dramatically, but in a milder form. During a period when two teammates were on leave and one had just resigned, I was effectively solo on a feature that was on the sprint commitment.</p><p>The first thing I did was scope it honestly. Not 'can I build everything in the original spec' but 'what is the minimum that delivers the value the stakeholder actually needs, and what's genuinely optional for this iteration?' I had that conversation early — not at the end of the sprint when it was too late to adjust expectations. The product owner was fine cutting two of five originally planned UI enhancements. What they actually needed was the core API and data model.</p><p>Then I focused hard. Fewer context switches, less time in Slack, longer focused blocks. Without the natural interruptions of a team working around you, solo periods can actually be quite productive if you're disciplined about it.</p><p>I also documented as I went — more than I normally would — because I knew I was the only one who'd know what I'd done, and if I needed to hand it off or someone needed to review it later, they'd have context.</p><p>I delivered about 70% of the original spec, with the most critical 70%. I'd call that a reasonable outcome given the circumstances, and I'd take that trade over promising 100% and delivering 60% late with stress.</p>",
  "followUps": [
    {
      "question": "When is it okay to escalate and ask for help vs just push through?",
      "answer": "<p>The signal for me is: am I blocked in a way I can't solve with time, or am I just behind schedule in a way I can solve with focus? The first case requires escalation because no amount of extra effort closes the gap. The second case usually just requires prioritization and honest communication about timelines. The mistake I used to make was waiting too long to escalate the first type, because it felt like admitting failure. I've learned it's the opposite — flagging early gives everyone options. Flagging late removes them.</p>"
    }
  ],
  "tip": "<strong>Solo delivery is about scope management, not heroics.</strong> The right answer isn't 'I'd work 18 hours a day to deliver everything.' It's 'I'd identify the critical 70%, communicate the tradeoff clearly, and deliver that reliably.' Sustainable output beats unpredictable heroism.",
  "tags": ["behavioral", "hr", "situational", "solo", "delivery"],
  "sortOrder": 45,
  "isActive": True
},

{
  "id": "beh-046",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "How would you handle an irate client or manager who questions your work?",
  "answer": "<p>My first instinct is: don't get defensive. Which sounds obvious until you're actually in that situation and someone is questioning something you spent two weeks building.</p><p>I had a close version of this when a client on CSInvoice raised a very sharp complaint in a sprint review — they'd found what looked like a data inconsistency in their invoice history and were clearly frustrated. The implication was that we'd introduced a bug.</p><p>What I did: I didn't immediately defend the code. I asked them to show me the specific example they were looking at. While they were showing me, I was taking notes, not building a counter-argument. Once I understood exactly what they were seeing, I said — honestly — 'I can see why that looks wrong. Let me investigate and come back to you by end of day with a clear explanation of what happened and whether it's a bug or expected behavior.' And I did.</p><p>Turned out it was expected behavior that wasn't communicated clearly — the invoice history showed voided invoices in a way that looked like errors but was correct. The problem was the UI, not the data. I explained it clearly and offered to make the voided state more visually distinct. The client came out of it satisfied because they were heard, investigated, and given a real answer quickly.</p><p>The principle: listen fully before responding, don't defend before understanding, commit to a timeline and hit it.</p>",
  "followUps": [
    {
      "question": "What if the complaint turns out to be valid — it really was your bug?",
      "answer": "<p>Then I own it directly. 'You're right, this is a bug I introduced. Here's specifically what happened, here's my fix, here's what I'm putting in place to catch this type of issue in the future.' No minimizing, no explaining why it was hard to avoid. Clients and managers respect accountability far more than they respect deflection. The bug is done — the only question is how you handle it after.</p>"
    }
  ],
  "tip": "<strong>Listen before defending.</strong> Most irate stakeholders calm down when they feel genuinely heard. Jumping to 'the code is correct' before understanding their concern makes things worse even when you're right.",
  "tags": ["behavioral", "hr", "situational", "client", "conflict"],
  "sortOrder": 46,
  "isActive": True
},

{
  "id": "beh-047",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "If you were given a role in a new domain tomorrow, how would you approach it?",
  "answer": "<p>I've actually been in a version of this. When I started on FolioTrack, I had no financial domain knowledge — I didn't understand NAV calculations, mutual fund structures, ISIN codes, or how portfolio rebalancing worked. I was hired for .NET and Angular skills, not finance domain expertise.</p><p>What worked:</p><p><strong>Domain first, code second.</strong> Before I wrote a line of code I spent the first week reading — not technical docs, but actual domain material. How do mutual funds work? What does NAV mean? What are the user workflows in portfolio management? Understanding the problem you're solving makes every technical decision downstream better. I asked stupid questions to the product owner on purpose in the first few weeks, because once the project was in flight there wouldn't be space for them.</p><p><strong>Find the domain expert and stay close to them.</strong> The product owner on FolioTrack had actual finance industry experience. I made it a point to understand their mental model, not just their requirements. That context changed how I designed certain data structures because I understood the underlying business logic rather than just implementing a spec.</p><p><strong>Build something small, fast.</strong> Rather than trying to understand everything before writing code, I'd try to get a small but real piece working quickly — usually something end-to-end, even if narrow. It forces you to confront the actual complexity rather than imagining it.</p>",
  "followUps": [
    {
      "question": "What new domain would you find most interesting to work in?",
      "answer": "<p>Healthcare or financial risk. Both have high-stakes data, interesting regulatory constraints, and domain logic that's genuinely complex — not just a CRUD app with a different label. The kind of domain where the business logic is hard because the problem is hard, not because it was designed badly. I've had a taste of financial domain work with FolioTrack and CSInvoice, and I find the intersection of precise business rules and software design genuinely interesting.</p>"
    }
  ],
  "tip": "<strong>Show curiosity and a learning method, not just reassurance that you can adapt.</strong> 'I'm a fast learner' is unconvincing. 'Here's specifically how I approached learning a domain I was new to, and here's what worked' is a story that actually demonstrates the capability.",
  "tags": ["behavioral", "hr", "situational", "new-domain", "learning"],
  "sortOrder": 47,
  "isActive": True
},

{
  "id": "beh-048",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "low",
  "question": "How would you manage reporting upwards when your manager is unavailable?",
  "answer": "<p>This comes up more than you'd expect — managers are in back-to-back meetings, on leave, or simply not reachable when something needs a decision.</p><p>My default: I've been burned by silence before. If I need a decision to proceed and my manager is unreachable, waiting indefinitely is usually the wrong call. What I'll do depends on the urgency and stakes.</p><p><strong>Low urgency:</strong> Document the question, my recommendation, and the information I have, and send it over Slack or email with a clear question and expected decision date. They can respond when available. I'll continue with other work or make a reversible decision in the meantime.</p><p><strong>Medium urgency:</strong> I'll go one level up if appropriate — contact their manager or a peer manager who has context. I'd flag that I'm doing it: 'Sarah's unavailable and this is blocking [X], so I'm looping in [name] for this specific decision.' Transparency prevents this from looking like I'm going around anyone.</p><p><strong>High urgency, production issue:</strong> I act first, inform after. If something is breaking in production and waiting for manager approval is making it worse, I stabilize the situation and document what I did and why. Better to explain a decision after the fact than to ask permission while things get worse.</p><p>The principle across all cases: don't let a management communication gap become a project delay if there's a reasonable path forward.</p>",
  "followUps": [
    {
      "question": "How do you make sure you have enough context to make good decisions in your manager's absence?",
      "answer": "<p>Continuous context-building is better than cramming before an absence. I try to understand the why behind the decisions my manager makes — not just what they decided but why, what constraints they were balancing. When I understand that, I can make decisions in the same spirit when they're unavailable. The managers I've worked with who are clear about their reasoning — even for small decisions — create teams that operate better independently than ones who just direct without explaining.</p>"
    }
  ],
  "tip": "<strong>Show you can operate independently without acting recklessly.</strong> The right answer isn't 'I wait' (shows dependency) or 'I just make all decisions myself' (shows disregard for process). It's 'I match the action to the stakes and keep everyone informed.'",
  "tags": ["behavioral", "hr", "situational", "reporting", "independence"],
  "sortOrder": 48,
  "isActive": True
},

{
  "id": "beh-049",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "medium",
  "question": "Suppose your promotion is delayed for unknown reasons — what would you do?",
  "answer": "<p>First — I'd want to understand why, specifically. 'Unknown reasons' is not an answer I'd accept passively. I'd have a direct, professional conversation with my manager: 'Can you help me understand what needs to happen for this to move forward, and what the timeline looks like?' Not aggressive — but clear that I want a concrete answer, not reassurance.</p><p>If the reason is something I can act on — a skill gap, a visibility issue, a specific project outcome they need to see — then I have a path forward and I'll work it explicitly. I'd want written or at least verbal agreement on: here's what success looks like, here's the timeline for the next conversation.</p><p>If the reason is structural — budget freeze, headcount cap, internal politics — then I need to make a decision about whether to stay and wait, or move on. I'd give it a defined time window, not indefinitely. 'If there's no movement in the next 3 months, I'll re-evaluate my options' is a concrete position, not an ultimatum delivered to my manager, but a private decision I've made for myself.</p><p>What I won't do: stew silently while hoping things change, or get cynical and disengage. Both are bad for me and the team. If I'm going to stay, I stay fully engaged. If I'm going to go, I go with appropriate notice and professionalism.</p>",
  "followUps": [
    {
      "question": "Have you been in a situation where you felt your growth was blocked? How did you handle it?",
      "answer": "<p>Yes — and this is actually part of why I'm looking now. The path to senior developer in my current company isn't unclear because I haven't performed — it's unclear because the senior positions are occupied and the company isn't growing fast enough to create new ones. I had the conversation, got honest feedback that the constraint was structural, and decided I'd rather invest my growth years somewhere with more headroom. That's a rational decision, not a resentful one.</p>"
    }
  ],
  "tip": "<strong>Show agency — not passivity, not aggression.</strong> Waiting and hoping is weak. Demanding a promotion is tone-deaf. Asking for clear criteria, holding to a personal timeline, and making a rational decision based on the outcome is what mature career management looks like.",
  "tags": ["behavioral", "hr", "situational", "promotion", "career"],
  "sortOrder": 49,
  "isActive": True
},

# ─── OFFER DECISION FINALIZATION ─────────────────────────────────────────────

{
  "id": "beh-050",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "Are you interviewing elsewhere? If yes, how far along are you?",
  "answer": "<p>Yes, I'm interviewing at a couple of other companies — I'll be straightforward about that because I think it's more respectful of everyone's time than pretending otherwise.</p><p>In terms of how far along: I'm at early to mid stages elsewhere — I've had initial conversations but no offers on the table yet. This process with you is one I'm genuinely interested in, not just using as a benchmark.</p><p>I want to be honest for two reasons: first, it's the truth and I'd rather start a potential working relationship without being evasive. Second, if there's urgency on your side or mine, it's better to know that upfront so we can manage the process accordingly.</p><p>I'm not trying to create artificial pressure — I don't have a competing offer right now, so there's no manufactured deadline. But I am actively in conversations and I'm hoping to make a decision within the next 4-6 weeks ideally.</p>",
  "followUps": [
    {
      "question": "What would make you choose us over another offer?",
      "answer": "<p>Honestly — the quality of the work and the team. If the technical problems are interesting, the team has strong engineers I can learn from, and the growth path is clear, that matters more to me than a marginal salary difference. I'm also looking for stability — I want to be somewhere I can put in 2-3 years and grow meaningfully, not somewhere I'm re-evaluating in 12 months. I'd want to understand the team dynamics, how technical decisions get made, and what 'senior developer' looks like in your organization before I could give you a fully confident answer. But the role as described is genuinely compelling.</p>"
    }
  ],
  "tip": "<strong>Be honest that you're interviewing elsewhere — but don't use it as leverage unless you have a real competing offer.</strong> Vague 'I have other options' without substance sounds like a bluff. 'I'm at early stages elsewhere and genuinely interested here' is credible and transparent.",
  "tags": ["behavioral", "hr", "offer", "interview-process", "transparency"],
  "sortOrder": 50,
  "isActive": True
},

{
  "id": "beh-051",
  "category": "behavioral",
  "difficulty": "easy",
  "frequency": "very-high",
  "question": "What is your notice period, and are you willing to negotiate it?",
  "answer": "<p>My contractual notice period is [X days/months]. In practice, how flexible that is depends on a few factors.</p><p>On the current employer's side: if they need me for a critical handover or release, I'd be willing to stay the full period and do a thorough transition — proper documentation, knowledge transfer sessions, making sure whoever takes over my work has context. I'd rather leave cleanly than leave a mess that follows my reputation.</p><p>On your side: if there's urgency to fill the role and an earlier start would be genuinely valuable, I'd have an honest conversation with my current manager about whether an earlier release is feasible. Most companies are flexible if you give them enough lead time and make the handover clean — it's when people leave abruptly that it creates problems.</p><p>My honest preference is to serve the full notice period because it's the professional thing to do and the right way to leave. But I'm open to a conversation if your timeline is genuinely tight, and I'd approach it transparently with both parties rather than just disappearing.</p>",
  "followUps": [
    {
      "question": "What will you do during your notice period?",
      "answer": "<p>Document everything that only I know — undocumented systems, historical decisions that aren't in tickets, the context behind why certain things were built the way they were. Do proper knowledge transfer with whoever is taking over my work. And close out or hand off anything that's in flight so it doesn't get dropped. I don't believe in mentally checking out once I've given notice — that period is part of the professional relationship and I'd want to handle it well regardless of how the exit conversation went.</p>"
    }
  ],
  "tip": "<strong>Give a real answer about flexibility — don't just say 'I'm negotiable' without context.</strong> Explaining what would make an early exit feasible (clean handover, current employer's flexibility) shows you've thought about it practically, not just said the easy answer.",
  "tags": ["behavioral", "hr", "notice-period", "offer", "joining"],
  "sortOrder": 51,
  "isActive": True
},

{
  "id": "beh-052",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "high",
  "question": "What's your ideal job role and why?",
  "answer": "<p>Somewhere between senior developer and tech lead — hands-on with code, but contributing to design and architecture decisions, not just implementing them.</p><p>More specifically: I want to be the person who takes a business problem and figures out how to structure the technical solution — what the data model looks like, where the complexity lives, what the API contract should be, how the moving pieces fit together. Then I want to do a significant chunk of the implementation myself, not just hand it off. I don't want to move fully into management — I like the craft of writing code — but I want my technical decisions to have broader impact than a single feature ticket.</p><p>In terms of domain: I'm most comfortable with backend-heavy .NET work where there's real business logic complexity. I can work across the stack — Angular, SQL, infrastructure — but my strongest contributions are in the backend and data layer. The ideal role plays to that while giving me surface area on the other layers.</p><p>In terms of team: I want to work with people who take code quality seriously — not in a pedantic way, but in a 'we care about whether this will be maintainable in two years' way. Teams like that make me better.</p><p>This role, as I understand it, looks like a good fit for that profile — which is why I'm here.</p>",
  "followUps": [
    {
      "question": "Where do you see the boundary between senior developer and tech lead?",
      "answer": "<p>For me, it's about scope of influence rather than technical skill level. A senior developer makes great decisions for their own work. A tech lead shapes the technical decisions for the team's work — standards, patterns, architectural direction, code review quality. The tech lead role also involves more stakeholder communication — explaining technical decisions upward and translating business requirements downward. I'm building toward the second, but I'm realistic that it's a function of trust and track record within a team, not just a title I can claim by skill level alone.</p>"
    }
  ],
  "tip": "<strong>Name something specific — not just 'a challenging role with a good team.'</strong> Describe the work you want, the level of ownership you're looking for, and where your technical strengths fit. This is a differentiation question dressed up as a preference question.",
  "tags": ["behavioral", "hr", "career-goals", "ideal-role", "offer"],
  "sortOrder": 52,
  "isActive": True
},

{
  "id": "beh-053",
  "category": "behavioral",
  "difficulty": "medium",
  "frequency": "medium",
  "question": "What's one non-negotiable factor for you in your next role?",
  "answer": "<p>If I'm being completely honest: technical quality culture.</p><p>What I mean by that: a team where code review is substantive and not just a rubber stamp, where there's some investment in making the codebase better over time rather than just shipping faster at the cost of everything else, where 'we'll clean it up later' is occasionally said and occasionally actually happens.</p><p>This matters to me beyond just aesthetic preference. Low-quality codebases are harder to work in, slower to iterate on, and more likely to produce the kind of production bugs that wake you up at night. The teams that take quality seriously, in my experience, also tend to take engineering in general more seriously — they invest in good tooling, they give developers time to learn, they treat technical debt as a real risk rather than a vague complaint.</p><p>I've worked in environments on both sides of this and the difference in day-to-day experience is significant. I'm not saying every line of code needs to be perfect — I've shipped pragmatic code under deadline pressure and I'll do it again. But I need the team to care about quality as a value, even if they can't always honor it completely.</p><p>Secondary to that: clear ownership. I want to know what I'm responsible for and have the latitude to make decisions within that scope without constant approval chains.</p>",
  "followUps": [
    {
      "question": "What would make you leave a new role quickly?",
      "answer": "<p>A culture where problems are known but nobody's willing to address them. Technical debt that everyone complains about in private but nobody's allowed to reduce. Processes that exist to protect people from accountability rather than to actually improve outcomes. Those environments don't get better over time — they just normalize. I've learned to read for those signals early in an interview process, and I'd ask about them directly rather than find out after joining.</p>"
    }
  ],
  "tip": "<strong>One clear, honest non-negotiable is more impressive than a list of preferences.</strong> It tells the interviewer what you actually value. 'Technical quality culture' or 'engineering ownership' or 'remote flexibility' — pick the real one, not the polite one.",
  "tags": ["behavioral", "hr", "non-negotiable", "values", "offer"],
  "sortOrder": 53,
  "isActive": True
},

{
  "id": "beh-054",
  "category": "behavioral",
  "difficulty": "hard",
  "frequency": "very-high",
  "question": "Why should we hire you and not the other candidates?",
  "answer": "<p>I'll answer this directly rather than with false modesty.</p><p>There are probably candidates who are better at algorithmic problem-solving than I am. There are probably candidates with broader exposure to more technologies. I'm not going to pretend otherwise.</p><p>What I think I specifically bring:</p><p><strong>Full-stack delivery without handoffs.</strong> I can take a feature from the API design through the data layer to the Angular component and deploy it. I don't stop at the boundary of my 'lane' and wait for someone else. On a smaller team where that kind of end-to-end ownership matters, that's valuable.</p><p><strong>Production experience, not just project experience.</strong> I've fixed things that were broken in production, with real users affected. I've debugged slow queries in live databases, shipped hotfixes under pressure, dealt with deployment failures. That kind of experience changes how you write code upfront — you think about failure cases differently when you've lived through them.</p><p><strong>I actually care about this specific role.</strong> I've done research on your product, your stack, and the kind of problems this team works on. I'm not applying to 50 generic .NET roles and hoping one lands. I'm here because the work you're doing is specifically interesting to me and I think my background is a genuine fit, not just a technical match on paper.</p><p>Hire me because you need someone who delivers reliably, takes ownership, and will invest in getting good at the specific problems your team works on. That's what I'll do.</p>",
  "followUps": [
    {
      "question": "What's one thing about you that won't come through in a standard interview?",
      "answer": "<p>How much I care about the code after it ships. In an interview you see how I approach problems and communicate. What you don't see is that I'm the person who checks production logs after a deploy, who notices when a query is getting slower over months and says something before it's a problem, who writes the documentation nobody asked for because the next person who works on this will need it. That kind of sustained attention to quality doesn't show up in a 2-hour interview, but it's the thing that makes the difference between code that works on day one and code that's still working in year three.</p>"
    }
  ],
  "tip": "<strong>Be direct and specific — this is not the time for false modesty.</strong> Name what you bring, own it clearly, and connect it to what they actually need. Generic 'I'm hardworking and passionate' answers are forgettable. Specific capabilities + evidence + genuine interest in the role is the answer that lands.",
  "tags": ["behavioral", "hr", "closing", "differentiation", "offer"],
  "sortOrder": 54,
  "isActive": True
}

]

# Append new questions to existing
data['questions'].extend(new_questions)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done. Total questions: {len(data['questions'])}")
print(f"New questions added: {len(new_questions)}")
