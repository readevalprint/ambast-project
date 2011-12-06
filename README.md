# Ambast
Amb = McCarthy's amb that this project initially used.

AST = Pythons Abstract Syntax Tree

This experiment was based on a fever dream I had in the desert where a lone wolf howled, "code begets code".

I am the wolf.

This is a generator of python code. It does this by paresing out the signifigant elements of an example code string.
It will interchange numbers, with numbers:

    1 + 2
    
will yield:

    1 + 1
    1 + 2
    2 + 1
    2 + 2

because it will see that it is possible to have a number on both sides of a Binary opreration (the +).

Here we see it will also interchange signs with signs:
        a + (a * a)

will lead to:

        (a * a)
        (a * (a * a))
        (a * (a * (a * a)))
        (a * (a * (a + a)))
        (a * (a + a))
        (a * (a + (a * a)))
        (a * (a + (a + a)))
        (a + a)
        (a + (a * a))
        (a + (a * (a * a)))
        (a + (a * (a + a)))
        (a + (a + a))
        (a + (a + (a * a)))
        (a + (a + (a + a)))

because it will understand that the lft side of a binary operator (the + or *) can have a variable, and the right side can have an expression. 

The only expression it knows is more binary operations.

More examples
[example1.txt](https://github.com/readevalprint/ambast-project/blob/master/example1.txt)
[example2.txt](https://github.com/readevalprint/ambast-project/blob/master/example2.txt)

# Usage
Dont.

If you must....

        >>> import ambast
        >>> ambast.print_possible('if a: print b\nelse:pass', width=1, depth=5)
        print a
        ##########
        print b
        ##########
        if a:
            print a
        else:
            pass
        ##########
        if a:
            print b
        else:
            pass
        ##########
        if b:
            print a
        else:
            pass
        ##########
        if b:
            print b
        else:
            pass
        ##########

# Problems
Tons. No optimizations on redundant or unreachable code. For example:

        if a:
            pass
            pass # Yeah we get it
        else:
            pass
or

        if a:
            return a
            some_code_that_will_not_run
        else:
            pass

Held all in memory. It will  _easily_ use all your ram.
For a var to be reconized as a function, it **must** be called with args and kwargs.
`else:` is required even if it just contains `pass`. This could be fixed in codegen.

Plus much much more. Much More.

## License
Haha foools!
