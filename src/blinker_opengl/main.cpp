#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <cmath>
#include <cstdlib>

int main(int argc, char** argv) {
    // Check if frequency argument is provided
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <frequency>" << std::endl;
        return -1;
    }

    // Parse frequency from command-line argument
    double frequency = std::atof(argv[1]);
    if (frequency <= 0) {
        std::cerr << "Invalid frequency. Frequency must be a positive number." << std::endl;
        return -1;
    }

    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    // Create a windowed mode window and its OpenGL context
    GLFWwindow* window = glfwCreateWindow(640, 480, "Blinking App", NULL, NULL);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    // Make the window's context current
    glfwMakeContextCurrent(window);

    // Initialize GLEW
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        return -1;
    }

    double lastTime = glfwGetTime();
    double lastFrameTime = lastTime;
    int frameCount = 0;
    bool colorToggle = false;

    // Loop until the user closes the window
    while (!glfwWindowShouldClose(window)) {
        double currentTime = glfwGetTime();
        double elapsedTime = currentTime - lastTime;
        double frameTime = currentTime - lastFrameTime;

        // FPS calculation and display
        frameCount++;
        if (frameTime >= 1.0) {
            std::cout << "FPS: " << frameCount << std::endl;
            frameCount = 0;
            lastFrameTime = currentTime;
        }

        // Check if it's time to toggle the color
        if (elapsedTime >= (1.0 / frequency)) {
            colorToggle = !colorToggle;
            lastTime = currentTime;
        }

        // Render the color
        if (colorToggle) {
            glClearColor(.0f, 0.0f, 0.0f, 1.0f); // Red
        } else {
            glClearColor(1.0f, 1.0f, 1.0f, 1.0f); // Blue
        }
        glClear(GL_COLOR_BUFFER_BIT);

        // Swap front and back buffers
        glfwSwapBuffers(window);

        // Poll for and process events
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
