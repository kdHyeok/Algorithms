#include <iostream>
#include <string>
#include <algorithm>

using namespace std;

int n;

void hanoi(int N, int from, int temp, int to)
{
    if (N == 1)
    {
        cout << from << " " << to << '\n';
        return;
    }
    hanoi(N - 1, from, to, temp); // 1 3 2
    cout << from << " " << to << '\n';
    hanoi(N - 1, temp, from, to); // 2 1 3
}

int main()
{
    cin >> n;

    string ans = "1"; // 1의 자리가 ans[0]에 오도록 유지

    for (int i = 0; i < n; i++)
    {
        int carry = 0;
        // 1의 자리부터 차례대로 2를 곱함
        for (char &c : ans)
        {
            int temp = (c - '0') * 2 + carry;
            c = (temp % 10) + '0'; // 현재 자리수 갱신
            carry = temp / 10;     // 올림수
        }
        // 마지막에 올림수가 남았다면 뒤에 붙임 (자릿수 확장)
        if (carry)
            ans += (carry + '0');
    }

    ans[0] -= 1;                     // 1의 자리는 항상 맨 앞에 있으므로 바로 뺄셈 가능
    reverse(ans.begin(), ans.end()); // 출력 직전에 딱 한 번만 뒤집기

     

    cout << ans << '\n';

    if (n <= 20)
    {
        hanoi(n, 1, 2, 3);
    }
}