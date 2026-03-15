Here are the absolute essential rules you need to know to parse and display the data correctly:

### 1. The Rx'd vs. Scaled Hierarchy (The Golden Sorting Rule)

Athletes can choose to do a workout exactly as prescribed (**Rx'd**) or with modified weights and movements (**Scaled**).

* **The Data Impact:** You cannot simply sort a workout column by "highest reps" or "fastest time." *Any* Rx score strictly outranks *every* Scaled score. An athlete who completes exactly 1 rep of an Rx workout will place higher on the leaderboard than an athlete who finishes the entire Scaled workout in record time. Your database needs a flag (e.g., `is_scaled: boolean`) to group and sort these tiers separately.

### 2. The Point System (Lowest Score Wins)

The overall Open leaderboard does not use an absolute measurement of fitness; it uses a relative ranking system.

* **The Data Impact:** Your rank in a specific workout becomes your "points" for that workout (e.g., finishing 10th worldwide gives you 10 points; finishing 500th gives you 500 points). The overall winner is the athlete with the **lowest** total points across all workouts.

### 3. The Three Raw Scoring Formats

Depending on the week, the Open measures fitness in one of three ways, which means your raw data format will change per column.

* **AMRAP (As Many Reps As Possible):** The score is an integer representing total reps. Higher is better.
* **For Time:** The score is a time duration (MM:SS). Lower is better. However, if an athlete hits the time cap before finishing, their score usually converts into a total rep count instead of a time.
* **For Load:** The score is a maximum weight lifted (usually in pounds). Higher is better.

### 4. Tiebreaks (The Secondary Sort)

Because thousands of people might get the exact same score on an AMRAP workout, CrossFit uses built-in tiebreak times to separate them.

* **The Data Impact:** A tiebreak is usually the time an athlete finished a specific earlier section of the workout. When sorting athletes who have identical rep scores, the athlete with the *lower* tiebreak time wins. This is critical for calculating precise percentiles.

### 5. Divisions (Your Core Filters)

Athletes are rigidly bucketed into divisions based on Sex and Age (e.g., Individual Men, Women 35-39, Boys 14-15).

* **The Data Impact:** An overall global rank across all humans doesn't exist natively. To calculate an athlete's accurate quantile or rank, your dashboard must first filter the dataset by their specific Sex and Age division.
