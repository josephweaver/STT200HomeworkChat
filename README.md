# STT200HomeworkChat
Homework chat intends to translate homeworks into conversations by which the students can use AI to explore the questions and concepts, all the while be assessed on 4 learning critera:

 - Correctness
 - Justification
 - Interpretation
 - Effort

## Use Case
A student is assigned a homework conversation in which they access the HomeworkChat via link in their content management system. A browser is opened and a LLM presents the student with a question based on a teacher provided homework.  The student attempts to cercumvent learning by writing the correct/incorrect answer.  
The grader AI detect the barebone attempt scoreing them 0 on Justification, Interpretation, and Effort and 1 or 2 points for correctness with an explaination of what they did right and wrong. 
The Tutor AI then suggest to student how to make improvements and then prompts them for information that leads to correct answer.
The student tries again, this time more equipped to answer the problem.

## Features
  - *Dualling Tutor and Grader AI* - by which the Grader AI provides suggestion for improvement based only the users input (ignoring the tutor). Tutor AI then uses Grader prompts and user Prompts in an attempt to lead the student to full credit and excellent learning outcomes. 
  - *Text-based question writing* - to create new content, you simplily need to create a new text file telling the AI what you want to have question about.
  - *Automatic Assessment* - No manual grading required, assignments are automatically graded as the student attempts each question.
  - *Save/Restore* - The student can stop and start at any time.
  - Anti-Cheat - Several mechanism were added to the tutor AI's behavior to deminish and or discourage cheating. 

## Future
  - Voice to Text, Text to Voice option - allows people with disabilities or simply perfer talking to engage.
  - Translation to native language - Allows non-english speakers to use the system
  - Question Variation - By purposing a single question we can allow the AI To create variations on the question of a simplier format.
  - Data Variation - We can provide a data set, then ask the AI to create variations on the dataset so no two student get the same question.
  - Evaluation Criteria: "AI Assistance Needed" - we can evalate how much AI assistance was need and provide an inverse rating regard how much AI assistance was needed, thus encourgaing them to not lean on the AI prompts too much.
  - Restart mechanism - The ability to clear the current conversation and start over in an attempt to get a better "AI Assistance Needed" grade.
  - Domain Specific Questioning - Allows a student to declare carreer goals, hobbies, and other interest that allow the LLM to custom tailor data and questions for the student to use in which they may be more engaged.
  - 
