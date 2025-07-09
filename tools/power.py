'''
A module to define the Power function 
'''
#! Power function definition
def power(base: float, exponent: float) -> float:
    """
    Calculate the power of a base number raised to an exponent.
    
    Args:
        base (float): The base number
        exponent (float): The exponent to raise the base to
        
    Returns:
        float: The result of base^exponent
        
    Raises:
        ValueError: If base is negative and exponent is fractional
        OverflowError: If the result is too large to represent
    """
    try:
        return base ** exponent
    except (ValueError, OverflowError) as e:
        raise e
