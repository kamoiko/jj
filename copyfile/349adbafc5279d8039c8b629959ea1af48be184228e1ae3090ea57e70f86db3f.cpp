#include <iostream>
#include <string>

using namespace std;

int main()
{
    while(1)
    {

        string str;
        cout<<"input :"<<endl;
        getline(cin,str);
        int cou=0;
        int negi=0;
        int ans=0;
        for(int i=0;i<str.size();i++)
        {
            if(str[i]=='(')
            {
                cou++;
            }
            if(str[i]==')')
            {
                cou--;
            }
            if(cou<ans)
            {
            ans=cou;
            }
        }
        ans*=-2;
        ans+=cou;
        cout<<"answer :"<<ans<<endl;
    }
    system("pause");
    return 0;
}

