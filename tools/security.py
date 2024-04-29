
class Security():

    def remove_characters(self, input_string, characters=None):
        """
        Removes specified characters from the input string. Then return a 
        tuple of the cleaned string and the unwanted characters found in a list
        Acces the cleaned string at the index 0 and the list of the unwanted characters 
        found at the index 1.

        The default characters it will remove are in the following list:
            characters_to_remove = [" ", ";", ",", "'", '"', '\\n', "#", "/", "\\", "%", "_", "--"]
            You can give a different list of characters as you want.

        Args:
            input_string (str): The input string.
            characters (list): List of characters to remove.

        Returns:
            str: The input string with specified characters removed.
        
        Usage:
            input_text = "Hello, world!_How are you? #Python is fun."
            cleaned_text = remove_characters(input_text, ["#", "_"])
            print("Cleaned text:", cleaned_text[0])
        """

        characters_to_remove = []
        unwanted_characters_found = []
        if characters == None:
            characters_to_remove = [" ", ";", ",", "'", '"', "\n", "#", "/", "\\", "%", "_", "--"]
        else:
            characters_to_remove = characters

        for char in characters_to_remove:
            if char in input_string:
                input_string = input_string.replace(char, "")
                unwanted_characters_found.append(char)


        return input_string, unwanted_characters_found




# print(Security.remove_characters("\nHello'"))
