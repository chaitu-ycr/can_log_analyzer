class App:
    """
    The App class demonstrates the four fundamental Object-Oriented Programming (OOP) concepts:

    - **Encapsulation**: Bundling data (attributes) and methods that operate on that data within a single unit (class).
    - **Abstraction**: Providing a simple interface and hiding complex implementation details from the user.
    - **Inheritance**: Allowing a class to inherit properties and methods from another class.
    - **Polymorphism**: Enabling different classes to be treated as instances of the same class through a common interface.

    Attributes:
        _name (str): The name of the application (encapsulated).
    """

    def __init__(self, name: str):
        """
        Initialize the App instance with a name.

        Demonstrates encapsulation by keeping the attribute private.

        Args:
            name (str): The name of the application.
        """
        self._name = name

    def run(self) -> None:
        """
        Run the application.

        Demonstrates abstraction: the user interacts with a simple interface
        without needing to know the internal details.
        """
        print(f"{self._name} is running.")

    def get_name(self) -> str:
        """
        Get the name of the application.

        Returns:
            str: The encapsulated name of the application.
        """
        return self._name


class AdvancedApp(App):
    """
    AdvancedApp extends App to demonstrate inheritance and polymorphism.

    Inherits from:
        App

    Overrides:
        run: Demonstrates polymorphism by providing a different implementation.
    """

    def run(self) -> None:
        """
        Run the advanced application with enhanced features.

        Demonstrates polymorphism by overriding the base class method.
        """
        print(f"Advanced features enabled for {self._name}. App is running with enhancements.")


if __name__ == "__main__":
    # Example usage demonstrating OOP concepts:
    app = App("BasicApp")
    app.run()  # Output: BasicApp is running.

    adv_app = AdvancedApp("ProApp")
    adv_app.run()  # Output: Advanced features enabled for ProApp. App is running with enhancements.