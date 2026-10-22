#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <conio.h>
#else
#include <termios.h>
#include <unistd.h>
// Simple non-blocking input for Unix-like systems
int kbhit() {
    struct timeval tv = { 0L, 0L };
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return select(1, &fds, NULL, NULL, &tv);
}
int getch() {
    struct termios oldt, newt;
    int ch;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    return ch;
}
#endif

using namespace std;

const int WIDTH = 4;   // 4 lanes like Piano Tiles
const int HEIGHT = 10; // Height of the game board

class PianoTilesGame {
private:
    vector<vector<int>> board;
    int score;
    bool gameOver;
    int speed; // Milliseconds per tick

public:
    PianoTilesGame() {
        board = vector<vector<int>>(HEIGHT, vector<int>(WIDTH, 0));
        score = 0;
        gameOver = false;
        speed = 400; // Initial speed
        srand(time(0));
    }

    // Add a new row at the top with one random tile
    void spawnRow() {
        // Shift all rows down
        for (int i = HEIGHT - 1; i > 0; --i) {
            board[i] = board[i - 1];
        }
        // Generate new top row
        vector<int> newRow(WIDTH, 0);
        int tileCol = rand() % WIDTH;
        newRow[tileCol] = 1; // 1 represents a tile
        board[0] = newRow;

        // Check if the bottom row had an unclicked tile (Game Over)
        for (int j = 0; j < WIDTH; ++j) {
            if (board[HEIGHT - 1][j] == 1) {
                gameOver = true;
            }
        }
    }

    // Render the game board to the console
    void draw() {
        #ifdef _WIN32
        system("cls");
        #else
        system("clear");
        #endif

        cout << "===================\n";
        cout << "   PIANO TILES     \n";
        cout << " Score: " << score << "\n";
        cout << "===================\n";

        for (int i = 0; i < HEIGHT; ++i) {
            cout << "|";
            for (int j = 0; j < WIDTH; ++j) {
                if (board[i][j] == 1) cout << "█";
                else cout << " ";
                cout << "|";
            }
            cout << "\n";
        }
        cout << "===================\n";
        cout << " Controls: A S D F \n";
    }

    // Handle user input for lanes 0, 1, 2, 3 (Keys: a, s, d, f)
    void handleInput(char input) {
        int col = -1;
        if (input == 'a' || input == 'A') col = 0;
        else if (input == 's' || input == 'S') col = 1;
        else if (input == 'd' || input == 'D') col = 2;
        else if (input == 'f' || input == 'F') col = 3;

        if (col != -1) {
            // Check the bottom-most row or close to it for the tile
            if (board[HEIGHT - 1][col] == 1) {
                board[HEIGHT - 1][col] = 0; // Clear the tile
                score++;
                // Speed up slightly every 10 points
                if (score % 10 == 0 && speed > 100) {
                    speed -= 25;
                }
            } else {
                // Pressed wrong lane -> Game Over
                gameOver = true;
            }
        }
    }

    bool isGameOver() const {
        return gameOver;
    }

    int getScore() const {
        return score;
    }

    int getSpeed() const {
        return speed;
    }
};

int main() {
    PianoTilesGame game;
    char input;

    cout << "Press any key to start Piano Tiles...\n";
    #ifdef _WIN32
    _getch();
    #else
    getch();
    #endif

    auto lastTime = chrono::steady_clock::now();

    while (!game.isGameOver()) {
        // Handle keyboard input non-blockingly
        #ifdef _WIN32
        if (_kbhit()) {
            input = _getch();
            game.handleInput(input);
        }
        #else
        if (kbhit()) {
            input = getch();
            game.handleInput(input);
        }
        #endif

        // Update board based on time elapsed
        auto currentTime = chrono::steady_clock::now();
        auto elapsed = chrono::duration_cast<chrono::milliseconds>(currentTime - lastTime).count();

        if (elapsed >= game.getSpeed()) {
            game.spawnRow();
            lastTime = currentTime;
        }

        game.draw();
        this_thread::sleep_for(chrono::milliseconds(50));
    }

    cout << "\nGame Over! Final Score: " << game.getScore() << "\n";
    return 0;
}
