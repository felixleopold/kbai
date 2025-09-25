#!/usr/bin/env python3
"""
Individual test runner for search.py functions.
Run this to test each function separately.
"""

from search import (
    test_is_terminal, 
    test_expand_children, 
    test_minimax, 
    test_complete_minimax_player
)

def main():
    print("INDIVIDUAL FUNCTION TESTING")
    print("=" * 50)
    print("Choose which test to run:")
    print("1. test_is_terminal() - Test terminal state detection")
    print("2. test_expand_children() - Test tree expansion") 
    print("3. test_minimax() - Test minimax algorithm")
    print("4. test_complete_minimax_player() - Test complete player")
    print("5. Run all tests")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == "0":
                print("Exiting...")
                break
            elif choice == "1":
                test_is_terminal()
            elif choice == "2":
                test_expand_children()
            elif choice == "3":
                test_minimax()
            elif choice == "4":
                test_complete_minimax_player()
            elif choice == "5":
                from search import run_all_tests
                run_all_tests()
            else:
                print("Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
