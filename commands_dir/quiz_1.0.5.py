import json
import random
import asyncio
from twitchio.ext import commands
import os
import time
import math
from collections import defaultdict

command_name = "quiz"
description = 'Gioco per la chat, "!quiz help" per i dettagli.'
enable_access_control = True
access_denied_message = "{ctx.author.name} non sei autorizzato ad eseguire questo comando!"

user_command_name = "q"

questions_file = "media/quiz.json"
current_question = 0
question_in_progress = False
quiz_running = False
leaderboard = defaultdict(int)

answered_users = {}
correct_responses = []
wrong_responses = []
correct_answer = None

answer_delay = 4
time_to_respond = 10

first_correct_points = +5
second_correct_points = +3
third_correct_points = +1
first_wrong_points = -3
second_wrong_points = -2
third_wrong_points = -1

help_message =  '"!quiz start" avvia il quiz, "!quiz next" scrive una domanda in chat, "!quiz stop" conclude il quiz.'
start_message = 'Il quiz è iniziato! "!quiz next" per visualizzare la domanda, "!q" per rispondere alle domande. Buona fortuna!'
stop_message = "Il quiz è terminato! Grazie per aver partecipato."
A_answer_message = "A - {}"
B_answer_message = "B - {}"
C_answer_message = "C - {}"
D_answer_message = "D - {}"
no_more_questions_message = 'Non ci sono più domande da visualizzare, "!quiz stop" per terminare il quiz.'
correct_answer_message = "La risposta corretta è {}"
time_to_respond_message = "Avete {} secondi per rispondere."
question_in_progress_message = "{ctx.author.name} aspetta che la domanda in corso sia completata."
quiz_running_message = "{ctx.author.name} il quiz è già avviato."
quiz_not_running_message = "{ctx.author.name} il quiz non è avviato."
file_not_found_message = "{ctx.author.name} file {questions_file} non trovato."
invalid_command_message = '{ctx.author.name} parametro "{command}" non riconosciuto.'
invalid_answer_message = '{ctx.author.name} risposta non valida. I valori accettati sono "a", "b", "c" e "d".'
already_answered_message = '{ctx.author.name} hai già risposto.'
current_question_message = "Domanda #{current_question}: {question}"
leaderboard_message_prefix = "Classifica parziale: "
final_leaderboard_message_prefix = "Classifica finale: "

with open("config.json", "r") as file:
    data = json.load(file)

with open("enabled_users.json", "r") as file:
    enabled_users = json.load(file)

questions_dir = os.path.dirname(questions_file)
if not os.path.exists(questions_dir):
    os.makedirs(questions_dir, exist_ok=True)

if not os.path.exists(questions_file):
    default_questions = [
        {
            "id": 1,
            "question": "domanda 1",
            "A_answer": "risposta A1",
            "B_answer": "risposta B1",
            "C_answer": "risposta C1",
            "D_answer": "risposta D1",
            "correct_answer": "A"
        },
        {
            "id": 2,
            "question": "domanda 2",
            "A_answer": "risposta A2",
            "B_answer": "risposta B2",
            "C_answer": "risposta C2",
            "D_answer": "risposta D2",
            "correct_answer": "D"
        }
    ]
    with open(questions_file, "w") as file:
        json.dump(default_questions, file, indent=4)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=data["token"],
            prefix=data["prefix"],
            initial_channels=data["initial_channels"],
        )

    async def event_ready(self):
        print(f"Command \"{command_name}\" loaded")

    @commands.command(name=command_name)
    async def handle_quiz(self, ctx: commands.Context):
        global current_question, quiz_running, question_in_progress, answered_users, correct_responses, wrong_responses, correct_answer
        user_lowercase = ctx.author.name.lower()
        if enable_access_control and user_lowercase not in enabled_users:
            await ctx.send(access_denied_message.format(ctx=ctx))
            return

        args = ctx.message.content.split()
        command = args[1].lower() if len(args) > 1 else "help"

        if command == "help":
            await ctx.send(f"{help_message}")
        elif command == "start":
            if not quiz_running:
                quiz_running = True
                current_question = 1
                answered_users = {}
                correct_responses = []
                wrong_responses = []
                correct_answer = None
                await ctx.send(f"{start_message}")
            else:
                await ctx.send(quiz_running_message.format(ctx=ctx))
        elif command == "next":
            if not quiz_running:
                await ctx.send(quiz_not_running_message.format(ctx=ctx))
            else:
                if not question_in_progress:
                    question_in_progress = True
                    answered_users = {}
                    correct_responses = []
                    wrong_responses = []
                    try:
                        with open(questions_file, "r") as file:
                            quiz_data = json.load(file)
                    except FileNotFoundError:
                        await ctx.send(file_not_found_message.format(ctx=ctx, questions_file=questions_file))
                        question_in_progress = False
                        return
                    if current_question > len(quiz_data):
                        await ctx.send(f"{no_more_questions_message}")
                        question_in_progress = False
                        return
                    else:
                        for q in quiz_data:
                            if q["id"] == current_question:
                                question = q["question"]
                                A_answer = q["A_answer"]
                                B_answer = q["B_answer"]
                                C_answer = q["C_answer"]
                                D_answer = q["D_answer"]
                                correct_answer = q["correct_answer"].lower()
                                break
                        await ctx.send(current_question_message.format(current_question=current_question, question=question))
                        await asyncio.sleep(answer_delay)
                        await ctx.send(A_answer_message.format(A_answer))
                        await asyncio.sleep(answer_delay)
                        await ctx.send(B_answer_message.format(B_answer))
                        await asyncio.sleep(answer_delay)
                        await ctx.send(C_answer_message.format(C_answer))
                        await asyncio.sleep(answer_delay)
                        await ctx.send(D_answer_message.format(D_answer))
                        await ctx.send(time_to_respond_message.format(time_to_respond))
                        await asyncio.sleep(time_to_respond)
                        await ctx.send(correct_answer_message.format(correct_answer.upper()))
                        full_leaderboard_message = leaderboard_message_prefix
                        for u, points in leaderboard.items():
                            full_leaderboard_message += f"{u} {points}, "
                        full_leaderboard_message = full_leaderboard_message.rstrip(", ")
                        await ctx.send(full_leaderboard_message)
                        current_question += 1
                        question_in_progress = False
                else:
                    await ctx.send(question_in_progress_message.format(ctx=ctx))
        elif command == "stop":
            if quiz_running:
                quiz_running = False
                current_question = 1
                await ctx.send(f"{stop_message}")
                final_leaderboard_message = final_leaderboard_message_prefix
                sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
                for u, points in sorted_leaderboard:
                    final_leaderboard_message += f"{u} {points}, "
                final_leaderboard_message = final_leaderboard_message.rstrip(", ")
                await ctx.send(final_leaderboard_message)
            else:
                await ctx.send(quiz_not_running_message.format(ctx=ctx))
        else:
            await ctx.send(invalid_command_message.format(ctx=ctx, command=command))

    @commands.command(name=user_command_name)
    async def handle_q(self, ctx: commands.Context, usr_answer: str):
        global answered_users, correct_responses, wrong_responses, leaderboard, correct_answer, quiz_running, question_in_progress
        user = ctx.author.name.lower()
        if not quiz_running:
            await ctx.send(quiz_not_running_message.format(ctx=ctx))
            return
        if question_in_progress:
            if user in answered_users:
                await ctx.send(already_answered_message.format(ctx=ctx))
                return

            if usr_answer.lower() not in ['a', 'b', 'c', 'd']:
                await ctx.send(invalid_answer_message.format(ctx=ctx))
                return

            if usr_answer.lower() == correct_answer:
                answered_users[user] = "correct"
                correct_responses.append(user)
                if len(correct_responses) == 1:
                    leaderboard[user] += first_correct_points
                elif len(correct_responses) == 2:
                    leaderboard[user] += second_correct_points
                elif len(correct_responses) == 3:
                    leaderboard[user] += third_correct_points
                else:
                    leaderboard[user] += 0
            else:
                answered_users[user] = "wrong"
                wrong_responses.append(user)
                if len(wrong_responses) == 1:
                    leaderboard[user] += first_wrong_points
                elif len(wrong_responses) == 2:
                    leaderboard[user] += second_wrong_points
                elif len(wrong_responses) == 3:
                    leaderboard[user] += third_wrong_points
                else:
                    leaderboard[user] += 0
        else:
            await ctx.send(quiz_not_running_message.format(ctx=ctx))

bot = Bot()
bot.run()
