if __name__ == '__main__':
    str = "I want to Remove all white \t spaces, new lines \n and tabs \t"

    new_string = ' '.join(str.split())
    print(new_string)

    list = [1,2,3]
    list.append(4)

    # def return2():
    #     return 1,2
    #
    # one,two = return2()
    # print(one)
    # print (two)

    class onetwo():
        def __init__(self,one,two):
            self.one = one
            self.two = two

    oneTwo = onetwo(1,2)
    print(oneTwo.one)

    str_1 = "All I Want is to parTy"
    assert ("Want" in str) == False
    assert ("want" in str_1.lower()) == True


