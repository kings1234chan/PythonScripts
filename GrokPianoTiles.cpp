#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <thread>
#include <chrono>
#include <string>

#ifdef _WIN32
    #include <conio.h>
    #include <windows.h>
#else
    #include <termios.h>
    #include <unistd.h>
    #include <fcntl.h>
#endif

using namespace std;

// ==================== Platform helpers ====================
#ifdef _WIN32
void clearScreen() { system("cls"); }
bool kbhit() { return _kbhit(); }
char getch() { return _getch(); }
void sleep_ms(int ms) { Sleep(ms); }
#else
void clearScreen() { system("clear"); }

int kbhit() {
    struct termios oldt, newt;
    int ch;
    int oldf;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);
    if (ch != EOF) {
        ungetc(ch, stdin);
        return 1;
    }
    return 0;
}

char getch() {
    char c;
    system("stty raw");
    c = getchar();
    system("stty cooked");
    return c;
}

void sleep_ms(int ms) {
    this_thread::sleep_for(chrono::milliseconds(ms));
}
#endif

// ==================== Game ====================
const int WIDTH = 4;
const int HEIGHT = 12;
const char TILE = '#';
const char EMPTY = ' ';
const char HIT = '*';

struct Tile {
    int lane;
    int row;
    bool active;
};

class PianoTiles {
private:
    vector<Tile> tiles;
    int score;
    int combo;
    int maxCombo;
    int misses;
    int speed;          // lower = faster
    int frame;
    bool gameOver;
    char keys[4] = {'a', 's', 'd', 'f'};

public:
    PianoTiles() {
        score = 0;
        combo = 0;
        maxCombo = 0;
        misses = 0;
        speed = 180;
        frame = 0;
        gameOver = false;
        srand(time(0));
    }

    void spawnTile() {
        Tile t;
        t.lane = rand() % WIDTH;
        t.row = 0;
        t.active = true;
        tiles.push_back(t);
    }

    void update() {
        frame++;

        // Move tiles down every few frames
        if (frame % 3 == 0) {
            for (auto& t : tiles) {
                if (t.active) t.row++;
            }
        }

        // Spawn new tile randomly
        if (frame % 8 == 0 && rand() % 100 < 70) {
            spawnTile();
        }

        // Check for missed tiles (reached bottom)
        for (auto& t : tiles) {
            if (t.active && t.row >= HEIGHT) {
                t.active = false;
                misses++;
                combo = 0;
                if (misses >= 5) gameOver = true;
            }
        }

        // Speed up gradually
        if (score > 0 && score % 15 == 0 && speed > 60) {
            speed -= 5;
        }

        // Clean inactive tiles
        tiles.erase(
            remove_if(tiles.begin(), tiles.end(),
                      [](const Tile& t) { return !t.active; }),
            tiles.end());
    }

    void handleInput() {
        if (!kbhit()) return;

        char c = tolower(getch());
        int lane = -1;

        if (c == 'a' || c == '1') lane = 0;
        else if (c == 's' || c == '2') lane = 1;
        else if (c == 'd' || c == '3') lane = 2;
        else if (c == 'f' || c == '4') lane = 3;
        else if (c == 'q' || c == 27) { // q or ESC
            gameOver = true;
            return;
        }

        if (lane == -1) return;

        // Find the lowest active tile in that lane
        int bestIdx = -1;
        int lowestRow = -1;
        for (int i = 0; i < (int)tiles.size(); i++) {
            if (tiles[i].active && tiles[i].lane == lane) {
                if (tiles[i].row > lowestRow) {
                    lowestRow = tiles[i].row;
                    bestIdx = i;
                }
            }
        }

        if (bestIdx != -1 && lowestRow >= HEIGHT - 4) { // only hit near bottom
            tiles[bestIdx].active = false;
            score++;
            combo++;
            if (combo > maxCombo) maxCombo = combo;
        } else {
            // Wrong press or too early
            combo = 0;
            misses++;
            if (misses >= 5) gameOver = true;
        }
    }

    void draw() {
        clearScreen();

        cout << "\n  ========== PIANO TILES ==========\n\n";
        cout << "  Score: " << score
             << "   Combo: " << combo
             << "   Max: " << maxCombo
             << "   Misses: " << misses << "/5\n\n";

        // Header
        cout << "     A       S       D       F\n";
        cout << "  +-------+-------+-------+-------+\n";

        for (int r = 0; r < HEIGHT; r++) {
            cout << "  |";
            for (int l = 0; l < WIDTH; l++) {
                bool hasTile = false;
                for (const auto& t : tiles) {
                    if (t.active && t.lane == l && t.row == r) {
                        hasTile = true;
                        break;
                    }
                }
                if (hasTile) {
                    cout << "  ###  |";
                } else {
                    cout << "       |";
                }
            }
            cout << "\n";
        }

        cout << "  +-------+-------+-------+-------+\n";
        cout << "\n  Controls: A S D F   |   Quit: Q\n";
        cout << "  Hit the tiles when they reach the bottom!\n";
    }

    void run() {
        cout << "Starting Piano Tiles in 2 seconds...\n";
        sleep_ms(2000);

        while (!gameOver) {
            handleInput();
            update();
            draw();
            sleep_ms(speed);
        }

        clearScreen();
        cout << "\n\n  ========== GAME OVER ==========\n\n";
        cout << "  Final Score : " << score << "\n";
        cout << "  Max Combo   : " << maxCombo << "\n";
        cout << "  Misses      : " << misses << "\n\n";
        cout << "  Thanks for playing!\n\n";
    }
};

int main() {
    PianoTiles game;
    game.run();
    return 0;
}
