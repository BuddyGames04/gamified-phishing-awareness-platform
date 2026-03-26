# User Manual

This manual explains how to use the phishing awareness training platform from a player’s perspective.

The platform is designed to help users practise phishing detection through repeated classification, contextual email evaluation, and user-generated phishing scenarios. The system includes three primary training modes: Arcade Mode, Inbox Simulator, and Player-versus-Player (PVP).

---

## 1. Accessing the Platform

Open the platform in your web browser:

http://localhost:3000

Or alternatively: 

https://gamified-phishing-awareness-platform.onrender.com/

You must log in or register before accessing the main menu.

User authentication allows the platform to track performance statistics, scores, and gameplay progress.

---

## 2. Main Menu

After logging in, the main menu provides access to the main features of the platform:

- **Arcade Mode**
- **Inbox Simulator**
- **PVP Mode**
- **Leaderboard**
- **Info Page**

A menu button (☰) provides access to profile information and logout options.

---

## 3. Arcade Mode

Arcade Mode provides rapid phishing classification practice.

### Objective

You are presented with an email and must decide whether it is:

- **Phishing**
- **Legitimate**

### How to Play

1. Select **Arcade Mode** from the main menu.
2. Read the displayed email.
3. Examine details such as:
   - sender address
   - subject line
   - message content
   - links or attachments
4. Choose **Phish** or **Not Phish**.
5. Immediate feedback will indicate whether your choice was correct.

### Notes

- Difficulty may adjust based on recent performance.
- Hints may appear after incorrect answers.
- The mode is designed for fast, repeated decision practice.

---

## 4. Inbox Simulator

The Inbox Simulator presents phishing detection within a simulated work inbox.

### Objective

Rather than evaluating a single email, you must work through a list of emails in a scenario-based inbox and identify phishing messages.

### How to Play

1. Select **Inbox Simulator** from the main menu.
2. Choose a scenario and level.
3. Read the scenario briefing.
4. Inspect the emails in the inbox.
5. Open emails and review their contents.
6. Decide whether each email is phishing or legitimate.
7. Complete the level to view your results.

### Notes

- Higher levels may contain more subtle phishing attempts.
- Some scenarios may include additional contextual information.
- Accuracy is prioritised over speed.

---

## 5. PVP Mode

PVP mode allows users to create phishing challenges and play challenges created by others.

### Creating a Challenge

Creating a challenge involves several steps:

1. **Create a Scenario**
   - organisation or company context
   - job role
   - department
   - scenario description

2. **Create a Level**
   - level title
   - briefing text

3. **Add Emails**
   Each email includes:
   - sender name
   - sender email
   - subject
   - message body
   - classification (phishing or legitimate)
   - difficulty level
   - optional links or attachments

4. **Publish or Save**
   - levels can be saved or published for others to play.

### Playing PVP Levels

1. Open **PVP Mode**
2. Browse available challenges
3. Select a level
4. Play the level using the inbox interface

---

## 6. Leaderboard

The leaderboard displays player rankings based on performance.

It allows users to:

- compare scores
- view relative rankings
- track progress compared with other players

Scores reward accuracy and successful completion of levels.

---

## 7. Profile

The profile page shows your personal performance statistics, including:

- number of attempts
- correct classifications
- incorrect classifications
- accuracy percentage
- other gameplay statistics

This information helps track improvement over time.

---

## 8. Info Page

The Info page provides reference information about phishing indicators and common attack techniques.

It can be used as a guide while learning to identify suspicious emails.

Topics may include:

- suspicious sender addresses
- urgency or pressure tactics
- unexpected attachments
- credential requests
- deceptive links

---

## 9. Feedback

The platform provides feedback to support learning.

### Arcade Mode

- Immediate correctness feedback
- Short hints explaining missed indicators

### Inbox Simulator and PVP

- Summary feedback after completing a level
- Explanation of key phishing indicators where relevant

---

## 10. Troubleshooting

### Unable to log in

Ensure the backend server is running and accessible.

### No data appears in the application

Check that:

- the backend service is running
- the database is available
- migrations have been applied
- the API base URL is correct

### Levels fail to load

Reload the page or restart the backend service.

---

## 11. Intended Use

This platform is a prototype research system developed as part of a University of Glasgow Honours Individual Project. It is intended for phishing awareness training and evaluation rather than deployment as a production security tool.