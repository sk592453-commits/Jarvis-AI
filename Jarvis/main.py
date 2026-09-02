from brain import ask_jarvis
from voice import listen, speak
from video import start_avatar_loop, set_avatar_state


def main():
    print("-" * 50)
    print("      J.A.R.V.I.S ONLINE")
    print("-" * 50)

    start_avatar_loop(mode="girl")

    while True:
        set_avatar_state("listening")
        user = listen()

        if not user:
            continue

        if user.lower() in ["exit", "quit", "shutdown"]:
            print("JARVIS: Goodbye.")
            set_avatar_state("speaking")
            speak("Goodbye.")
            set_avatar_state("idle")
            break

        try:
            answer = ask_jarvis(user)
            print("\nJARVIS: ", answer)
            set_avatar_state("speaking")
            speak(answer)
            set_avatar_state("listening")
        except Exception as e:
            print(f"\n❌ JARVIS: Error - {str(e)}")
            print("Please check your OpenAI API key and credits.")
            set_avatar_state("speaking")
            speak("Error. Please check your API key and credits.")
            set_avatar_state("listening")

if __name__ == "__main__":
    main()
