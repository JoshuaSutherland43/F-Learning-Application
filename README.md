# F# Exam Prep

> **A curriculum-driven, fully local F# study and examination preparation environment.**

F# Exam Prep is an interactive study application built around a university-level F# and functional programming module.

It combines structured concept learning, syntax reference, programming practice, automated F# code execution, exam simulation, progress tracking, weakness detection, structural-induction practice, lambda-calculus evaluation, and an interactive debugging environment — all running locally on your own machine.

The project was built to solve a simple problem:

> **What if exam preparation wasn't just reading notes, but an environment that could teach, test, analyse, and adapt to the way I study?**

---

## Highlights

* **14 curriculum topics** with seven levels of explanation per topic
* **34-entry searchable F# syntax reference**
* **Curriculum-driven practice questions** with automated grading
* **Real F# code execution** through `dotnet fsi`
* **Structural-induction proof engine**
* **Lambda-calculus parser and evaluator** with beta reduction and Church encodings
* **Timed and untimed exam simulation**
* **Adaptive weakness detection**
* **Progress and question-history tracking**
* **Interactive Code Lab**
* **Step-by-step debugging tutor**
* **SQLite persistence**
* **Fully local operation**
* **No accounts, subscriptions, or external AI APIs**

---

## Screenshots

> Add screenshots or a short demo GIF here.

### Dashboard

`<img width="1861" height="861" alt="image" src="https://github.com/user-attachments/assets/4bfe14d0-a1a0-440e-8d90-838579e8fc1a" />
`

### Practice & Code Lab

`<img width="1786" height="865" alt="image" src="https://github.com/user-attachments/assets/4475d555-8c7b-4f05-8258-53d99b4fe9bd" />
`

### Exam Mode

`<img width="1787" height="855" alt="image" src="https://github.com/user-attachments/assets/2620e856-8f97-43ef-af49-f5d446beccfa" />
`

### Progress & Weakness Detection

`<img width="1770" height="702" alt="image" src="https://github.com/user-attachments/assets/a5813043-5caf-4bfb-b7a3-45ac7f3e52e6" />
`

### Screen Recording
`https://github.com/user-attachments/assets/1676601f-f930-47cb-935f-5f2c2fbf83bd`

---

# Why I Built It

Preparing for a programming examination often involves jumping between lecture slides, notes, exercises, previous assessments, syntax references, and past papers.

I wanted to bring those activities into one environment.

The application was therefore designed around the complete learning cycle:

**Learn → Understand → Practise → Make mistakes → Analyse mistakes → Revisit weaknesses → Practise again → Simulate the exam**

The goal isn't simply to provide answers. It is to help develop the ability to recognise a problem, select an appropriate F# construct, reason about the solution, and implement it.

---

# Curriculum-Driven, Not Generic F#

A major design goal was to avoid building a generic F# tutorial and calling it exam preparation.

The application was developed by analysing the available module material, including:

* Lecture material
* Historical module notes
* Class tests
* Homework
* Class exercises
* Past examination papers

This was used to identify the actual concepts, programming patterns, question structures, and areas of emphasis within the module.

The application therefore distinguishes between **what belongs to the official curriculum** and material that is provided only as additional learning support.

---

# Supplementary Learning Resources

Three additional F# learning modules were also incorporated as **supplementary resources**.

These resources are intentionally kept separate from the official curriculum.

They can be used to:

* Expand explanations
* Provide alternative examples
* Clarify difficult concepts
* Provide additional context
* Strengthen conceptual understanding

They are **not presented as official examinable material** simply because they were included as references.

---

# Features

## Learn

Each curriculum topic provides structured explanations progressing from introductory understanding to exam-level application.

The explanation structure covers:

1. **What is it?**
2. **Syntax**
3. **How it works**
4. **Worked example**
5. **Variations**
6. **Exam application**
7. **Common mistakes**

This allows the same topic to be approached at different levels of depth.

---

## Syntax Reference

A searchable F# syntax reference provides quick access to commonly required constructs.

Entries explain:

**Syntax → Meaning → Example → Common Mistake → Exam Use**

This is designed to function as both a learning resource and a rapid revision reference.

---

## Practice

The practice engine provides curriculum-aligned questions across multiple formats, including:

* Multiple choice
* Code tracing
* Output prediction
* Programming questions
* Conceptual questions
* Debugging
* Algorithmic problem solving

Questions are parameterised where appropriate so that concepts can be practised without simply repeating the same question.

---

## Real F# Code Execution

Programming questions can execute submitted F# code using the .NET SDK's:

```text
dotnet fsi
```

This means code-writing questions are not graded solely by comparing strings or looking for predetermined keywords.

The submitted program can actually be executed and evaluated against the expected behaviour.

This same execution infrastructure powers the Code Lab.

---

# Structural Induction Engine

Structural induction received dedicated treatment because it is a significant component of the module's theoretical material.

The application includes:

* Structural-induction proof exercises
* Canonical proof structures
* Fill-in-the-justification activities
* Guided reasoning
* Proof validation

The objective is to practise the **structure of an induction proof**, rather than simply memorising completed proofs.

---

# Lambda Calculus Engine

The application includes a dedicated lambda-calculus engine capable of performing actual reductions.

It includes:

* Lambda-expression parsing
* Beta reduction
* Expression evaluation
* Church encodings
* Boolean operations

This allows lambda-calculus concepts to be explored interactively rather than only through static examples.

---

# Code Lab

The Code Lab provides an environment for experimenting with F# code.

When something goes wrong, the debugging tutor guides the learner through the problem rather than simply presenting corrected code.

The intended debugging workflow is:

**Identify the error → Understand why it occurs → Determine how to fix it → Test the correction**

---

# Exam Mode

Exam mode supports both:

* **Timed examinations**
* **Untimed practice examinations**

Questions can be selected according to the curriculum and appropriate difficulty.

After completing an examination, the application records:

* Overall performance
* Individual question results
* Topic performance
* Weak areas
* Question history
* Recommended areas for further revision

---

# Weakness Detection

The application tracks performance over time to identify recurring problems.

For example, repeated mistakes in a particular concept can be used to identify that topic as a weakness and direct the learner toward targeted practice.

This changes the study process from:

> "What should I study?"

to:

> "What am I consistently getting wrong?"

---

# Study Modes

The application currently provides:

| Mode           | Purpose                               |
| -------------- | ------------------------------------- |
| **Dashboard**  | Overview of progress and activity     |
| **Learn**      | Structured topic explanations         |
| **Practice**   | Curriculum-based exercises            |
| **Drill**      | Rapid concept and syntax practice     |
| **Weaknesses** | Targeted revision                     |
| **Exam**       | Timed and untimed examinations        |
| **Review**     | Review previous attempts and mistakes |
| **Explore**    | Interactive exploration of concepts   |
| **Code Lab**   | F# programming and debugging          |

---

# Content Labelling

Content is deliberately classified so that supplementary information is never silently presented as official course material.

### Official Curriculum

Content directly evidenced in the current course material and/or relevant examination material.

### Official but Not in Recent Exams

Genuine historical course content that was identified in the available module material but did not appear in the recent examination papers analysed.

### Supplementary

Additional material used to improve explanations or provide broader context.

Supplementary material is **not presented as evidence that the specific university module teaches or examines that content**.

---

# Architecture

```text
F# Exam Prep
│
├── backend/
│   ├── app.py
│   │   └── Flask API + routing
│   │
│   ├── curriculum.py
│   │   └── Topic content and explanation levels
│   │
│   ├── syntax_reference.py
│   │   └── Searchable F# syntax reference
│   │
│   ├── questions.py
│   │   └── Parameterised question templates
│   │
│   ├── induction_proofs.py
│   │   └── Structural-induction proof engine
│   │
│   ├── lambda_calc.py
│   │   └── Lambda-calculus parser/evaluator
│   │
│   ├── fsharp_runner.py
│   │   └── F# execution and grading
│   │
│   └── db.py
│       └── SQLite persistence
│
├── frontend/
│   ├── index.html
│   ├── *.js
│   └── *.css
│
└── ...
```

The frontend is implemented using plain HTML, CSS, and JavaScript with no frontend framework or build step.

The backend is powered by Python and Flask.

SQLite provides persistent storage for:

* Progress
* Question history
* Exposure tracking
* Exam results

---

# Question Architecture

Question generation is designed to be stateless.

A generated question carries the information required to evaluate the submitted response, allowing the question to travel between the server and browser without relying on traditional server-side session state.

For F# programming questions, submitted code can be executed through `dotnet fsi` and evaluated against the expected behaviour.

This provides a more meaningful assessment of programming solutions than simple textual comparison.

---

# Privacy & Local-Only Design

The application is designed to run entirely on the user's machine.

There is:

* No user account
* No subscription
* No external AI API
* No API key
* No cloud database
* No dependency on an external server at runtime

The application's study data is stored locally in:

```text
backend/study.db
```

This SQLite database contains local progress and study history.

Delete `study.db` to reset the application's stored progress.

---

# AI Usage

**The application itself does not use an AI service at runtime.**

The generated study content and functionality are implemented through deterministic application logic, including:

* Structured curriculum content
* Parameterised question generation
* A hand-written lambda-calculus interpreter
* Structural-induction logic
* F# execution and grading
* Rule-based feedback and study tracking

No ChatGPT, Claude, Gemini, or other AI API is required to run the application.

---

# Important: Public Repository Considerations

This project was developed around real university course material.

**The original source material is deliberately NOT included in this repository.**

This repository does not contain:

* Lecture slides
* Past examination papers
* Textbook PDFs
* Homework submissions
* Student numbers
* Private credentials
* Lecturer contact information

The application content was derived from analysing those resources, however, so the resulting curriculum structure and question styles may resemble the source module.

In particular:

* The topic selection reflects the actual module.
* The difficulty distribution was informed by available assessments.
* Question styles were informed by past examinations.
* No past examination question is intentionally reproduced verbatim.

If you are considering making a derivative version of this project for your own course, ensure that your use and redistribution of course material complies with your institution's policies and any applicable copyright restrictions.

When in doubt, keep the repository private.

---

# Security & Data

Before publishing, check the repository for personal information or credentials.

For example:

```bash
grep -rniE "your real name|student number|lecturer name" backend/ frontend/
```

Also verify that:

* `.env` files are excluded
* API keys are not committed
* Personal databases are excluded
* Generated local data is ignored
* Course source files are excluded
* Private university material is not accidentally committed

---

# Requirements

### Required

* **Python 3.10+**
* **.NET SDK** with `dotnet fsi` available

The .NET SDK is required because the application executes and evaluates F# code.

No external internet connection is required for the application itself once the required software dependencies are installed.

---

# Running the Application

## Windows — One Click

The repository includes:

```text
Start F# Exam Prep.vbs
```

Double-clicking the script starts the application in the background and opens it in your browser.

To stop the application:

```text
Stop F# Exam Prep.vbs
```

---

## Manual

From the repository root:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://localhost:5000
```

The server can be stopped with:

```text
Ctrl+C
```

---

# Data Persistence

Study progress is stored locally using SQLite:

```text
backend/study.db
```

The database is intentionally git-ignored.

Your progress therefore survives application restarts.

To reset the application completely, stop the server and delete:

```text
backend/study.db
```

The database will be recreated when the application starts again.

---

# Testing

The application was tested across the available curriculum and question types, including end-to-end workflows.

Testing included validation of:

* Topic navigation
* Question generation
* Question submission
* Automated grading
* F# code execution
* Exam mode
* Progress persistence
* Review history
* Weakness detection
* Lambda-calculus evaluation
* Structural-induction functionality
* Edge cases in question generation
* Database persistence

Several implementation issues were identified and corrected during development, including:

* F# list-literal formatting
* Type-redeclaration conflicts in the grading environment
* Boolean encoding in the review system
* Duplicate multiple-choice options
* Other question-generation and grading edge cases

---

# Project Status

**Complete and functional for local use.**

The application is currently designed specifically around the target F# module and its available learning and assessment material.

Future development could include:

* Additional curriculum support
* More question templates
* Expanded debugging functionality
* More sophisticated adaptive learning
* Additional functional-programming exercises
* Improved visualisation of learning progress

---

# Technology Stack

| Layer                | Technology                   |
| -------------------- | ---------------------------- |
| Backend              | Python                       |
| Web API              | Flask                        |
| Frontend             | HTML / CSS / JavaScript      |
| Database             | SQLite                       |
| F# execution         | .NET SDK / `dotnet fsi`      |
| Lambda calculus      | Custom Python implementation |
| Structural induction | Custom Python implementation |

---

# Project Philosophy

The application is built around a simple principle:

> **Don't just memorise the answer. Understand the problem, understand the syntax, understand the reasoning, and then solve it yourself.**

The ultimate goal is not to make programming easier by hiding the difficult parts.

It is to make the difficult parts **learnable**.

---

## License

Add your chosen licence here if you intend to distribute the project publicly.

If the repository is intended primarily as a portfolio or personal academic project, clearly state the permitted use of the source code and note that the original university course materials are not included.
