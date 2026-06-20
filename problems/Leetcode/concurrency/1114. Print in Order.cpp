class Foo {
    sem_t two;
    sem_t three;
    public:
        Foo() {
            // iniitialize the semaphores, first we pass a reference
            // then the first 0 indicates a flag that these are all shared between threads of one process
            // then the second 0 indicates how many permits start in the box
            sem_init(&two, 0, 0);
            sem_init(&three, 0, 0);
        }
    
        void first(function<void()> printFirst) {
            
            // printFirst() outputs "first". Do not change or remove this line.
            printFirst();
            sem_post(&two); // drop one card in box 2
        }
    
        void second(function<void()> printSecond) {
            
            sem_wait(&two);
            // printSecond() outputs "second". Do not change or remove this line.
            printSecond();
            sem_post(&three);
        }
    
        void third(function<void()> printThird) {
            
            sem_wait(&three);
            // printThird() outputs "third". Do not change or remove this line.
            printThird();
        }
    };