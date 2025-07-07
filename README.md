# Claude 4 Sonnet Mathematical Evaluation

## 📊 Project Overview

This repository contains the complete dataset and analysis tools for evaluating Claude 4 Sonnet's mathematical assessment capabilities. The research reveals how JSON field ordering forces premature decision-making in LLM evaluation tasks, resulting in systematic errors despite correct mathematical reasoning.

### Key Findings
- **100% accuracy** in detecting incorrect answers
- **91.9% success** on percentage questions (Category A)
- **76.8% success** on "how many" questions (Category B)
- **JSON structure flaw**: Model must decide before reasoning, causing 78 systematic errors

## 📁 Repository Structure

```
claude_4_sonnet_math_evaluation/
├── api/
│   ├── api_query.py
│   └── math_evaluation_responses.json
├── questions/
│   ├── A group and B group correct incorrect.txt
│   ├── A group and B group.txt
│   └── questions_500_with_answers.txt
├── test/
│   ├── analyzer.html
│   └── test_analysis_results.csv
├── README.md
└── paper.pdf
```

## 🔍 File Descriptions

### `/api` Directory

#### `api_query.py`
Python script for querying Claude 4 Sonnet API with the evaluation prompt. The script:
- Loads questions from the dataset
- Sends each question-answer pair to Claude for evaluation
- Requests JSON response with `correct` (boolean) and `reason` (string) fields
- Handles API rate limiting and error recovery
- Saves all responses to `math_evaluation_responses.json`

**Usage:**
```python
python api_query.py --input ../questions/questions_500_with_answers.txt --output math_evaluation_responses.json
```

#### `math_evaluation_responses.json`
Complete API responses from Claude 4 Sonnet containing:
- Question ID
- Original question and provided answer
- Claude's evaluation (`correct`: true/false)
- Claude's reasoning explanation
- Raw API response data
- Timestamp and processing metadata

### `/questions` Directory

#### `A group and B group correct incorrect.txt`
Ground truth file containing all 500 questions with their correct/incorrect status and the actual correct answers for incorrect entries. Organized by groups (A and B) with each question showing:
- Question number
- Question text (without the census paragraph)
- Provided answer
- Status (CORRECT/INCORRECT)
- For incorrect answers: the actual correct answer in parentheses

Format example:
```
1. What percentage were not Russian? 75.1% (CORRECT)
16. What percentage were neither Russian, Ukrainian nor German? 72.5% (INCORRECT - Correct: 38.9%)
```

#### `A group and B group.txt`
Raw question dataset organized by groups without answers. Contains:
- **GROUP A**: 250 percentage questions
  - Single negation: "What percentage were not X?"
  - Multiple negations: "What percentage were neither X nor Y?"
- **GROUP B**: 250 "how many" questions
  - Population calculations based on percentages

Questions are listed without their census paragraphs, showing only the question text. Each census dataset generates 31 questions for Group A and 31 questions for Group B.

#### `questions_500_with_answers.txt`
Complete exam-format version where each question includes:
1. Full census paragraph with population and ancestry data
2. The specific question
3. The provided answer

Example:
```
1. As of the census of 2010, there were 2,296,560 people, 812,954 households, and 770,281 families residing in the city. The population density was 1351 people per square kilometer. There were 842,553 housing units at an average density of 662 per square kilometer. 24.9% were of Russian, 19.4% Ukrainian, 16.8% German, 14.6% Bulgarian and 9.7% Italian ancestry.
What percentage were not Russian?
Answer: 75.1%
```

### `/test` Directory

#### `analyzer.html`
Interactive web-based analysis tool that:
- Loads ground truth from `A group and B group correct incorrect.txt`
- Loads Claude's responses from `math_evaluation_responses.json`
- Compares answers to identify matches/mismatches
- Calculates accuracy metrics for:
  - Overall performance
  - Category A vs Category B
  - Correct vs incorrect answer detection
- Visualizes error patterns and systematic biases

**Usage:** Open `analyzer.html` in a web browser and upload the required files.

#### `test_analysis_results.csv`
Comprehensive CSV analysis file containing 500 rows with the following columns:
- **Group**: A or B (question category)
- **Question No**: 1-500
- **Question**: The question text only (without census paragraph)
- **Answer**: The provided answer
- **Actual Status**: Ground truth (Correct/Incorrect)
- **AI Prediction**: Claude's evaluation (Correct/Incorrect)
- **Match Result**: Whether AI agreed with ground truth (Match/Mismatch)
- **Correct Answer**: The actual correct answer (only filled for incorrect questions)
- **AI Reasoning**: Claude's explanation for its evaluation

This file enables detailed statistical analysis and identification of systematic error patterns.

### 📄 `paper.pdf`
Full academic paper: "Evaluating Claude 4 Sonnet's Mathematical Assessment Capabilities: An Analysis of JSON Structure-Induced Errors and Systematic Patterns"

## 🚀 Getting Started

### Prerequisites
```bash
pip install anthropic pandas numpy
```

### Running the Evaluation
1. **Generate API responses:**
   ```bash
   cd api
   python api_query.py
   ```

2. **Analyze results:**
   - Open `test/analyzer.html` in your browser
   - Upload the ground truth and response files
   - Review accuracy metrics and error patterns

3. **Export detailed analysis:**
   - Use the analyzer to generate `test_analysis_results.csv`
   - Import into Excel/Sheets for further analysis

## 📈 Key Statistics

### Overall Performance
- Total questions: 500
- Valid evaluations: 498 (2 API errors)
- Total errors: 78
- Success rate: 84.3%

### Error Distribution
| Category | Questions | Errors | Success Rate |
|----------|-----------|---------|--------------|
| A (Percentage) | 248 | 20 | 91.9% |
| B (How many) | 250 | 58 | 76.8% |

### Perfect Asymmetry
- Incorrect answer detection: 100% (163/163)
- Correct answer evaluation: 76.3% (255/335)

## 🔬 Research Insights

### JSON Structure Problem
The evaluation prompt requires:
```json
{
  "correct": boolean,  // Must be filled FIRST
  "reason": "string"   // Filled SECOND
}
```

This ordering forces the model to commit to a decision before reasoning through the problem, causing systematic errors even when the mathematical analysis is correct.

### Systematic Patterns Discovered
1. **Cognitive Dissonance** (14 cases): Model correctly solves in reasoning but already committed to wrong boolean
2. **200-Unit Deviation** (26 cases): Consistent calculation error in Category B
3. **Combinatorial Complexity**: Error rate increases with number of entities in question

## 📄 License

This project is licensed under CC BY 4.0 - see the LICENSE file for details.

## 🔗 Related Resources

- **Hugging Face Dataset**: https://huggingface.co/datasets/Naholav/claude_4_math_evaluation_500
- **Research Paper**: Available as `paper.pdf` in this repository

## 🙏 Acknowledgments

Thanks to Anthropic for providing access to Claude 4 Sonnet API. This research was conducted independently to improve AI evaluation systems.
