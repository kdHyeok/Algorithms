#include <iostream>
#include <string>

using namespace std;

long long arr[500005];
long long set[500005];
long long cnt = 0;

void merge(int left, int mid, int right)
{
    int i, j, k, l;
    i = left;
    j = mid + 1;
    k = left;

    while (i <= mid && j <= right)
    {
        if (arr[i] <= arr[j])
        {
            set[k++] = arr[i++];
        }
        else
        {
            cnt += (long long)(mid - i + 1);
            set[k++] = arr[j++];
        }
    }

    if (i > mid)
    {
        for (l = j; l <= right; l++)
        {
            set[k++] = arr[l];
        }
    }
    else
    {
        for (l = i; l <= mid; l++)
        {
            set[k++] = arr[l];
        }
    }

    for (l = left; l <= right; l++)
    {
        arr[l] = set[l];
    }
}
void Msort(int left, int right)
{
    int mid = (left + right) / 2;

    if (left < right)
    {
        Msort(left, mid);
        Msort(mid + 1, right);
        merge(left, mid, right);
    }
}

int main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    int N;
    cin >> N;
    for (int i = 0; i < N; i++)
        cin >> arr[i];

    Msort(0, N - 1);

    // cout<<"( ";
    // for (int i = 0; i < N; i++)
    //     cout<<arr[i]<<" ";
    // cout<<")\n";
    cout << cnt;
}