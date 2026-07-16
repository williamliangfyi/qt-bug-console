#include "calc.hpp"
#include <iostream>

// NOTE: this file is deliberately mis-formatted so the "format" job fails first.
// Run ./run-ci-local.sh --fix to auto-format, then re-run to see it pass.
int main(){
        int   sum      = calc::add(2,3);
    int product=calc::multiply(4,5);
  std::cout << "sum=" << sum << " product=" << product << "\n";
        return 0;
}
