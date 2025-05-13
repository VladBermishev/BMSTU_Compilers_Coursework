#include <cstdio>
#include <clocale>
#include <codecvt>
#include <vector>
#include <string>
#include <cuchar>
#include <forward_list>
#include <list>
#include <ranges>
#include <format>

namespace basic_std{
    using string_type = std::u32string;
    using __abi_args_type = string_type::traits_type::char_type**;
    std::forward_list<string_type> pool;

    std::vector<string_type::pointer> convert_args(std::list<string_type>& args){
        std::vector<string_type::pointer> result(args.size(), nullptr);
        for(auto [result_value, value] : std::views::zip(result, args))
            result_value = value.data();
        return std::move(result);
    }

    extern "C"{
        void PrintI(int val){ printf("%d", val); }
        void PrintL(long val){ printf("%ld", val); }
        void PrintD(double val){ printf("%lf", val); }
        void PrintF(float val){ printf("%f", val); }
        void PrintS(string_type::const_pointer val){ printf("%ls", val); }

        string_type::pointer StringConcat(string_type::const_pointer lhs, string_type::const_pointer rhs){
            std::size_t __lhs_length = string_type::traits_type::length(lhs);
            std::size_t __rhs__length = string_type::traits_type::length(rhs);
            pool.emplace_front(__lhs_length + __rhs__length + 1, '\0');
            string_type::traits_type::copy(pool.front().data(), lhs, __lhs_length);
            string_type::traits_type::copy(std::next(pool.front().data(), __lhs_length), rhs, __rhs__length);
            return pool.front().data();
        }

        string_type::pointer StringCopy(string_type::const_pointer str){
            std::size_t __sz = string_type::traits_type::length(str);
            pool.emplace_front(__sz + 1, '\0');
            string_type::traits_type::copy(pool.front().data(), str, __sz);
            return pool.front().data();
        }

        std::size_t StringLength(string_type::const_pointer str){
            return string_type::traits_type::length(str);
        }

        void StringFree(string_type::const_pointer str){
            const auto&& __pred = [str](const string_type& value){ return value.data() == str; };
            if(std::size_t __removed = pool.remove_if(__pred); __removed > 1)
                throw std::runtime_error(std::format("StringFree bad free: removed {} identical items", __removed));
        }

        void Main(__abi_args_type argv, int len);
    }
}

int main(int argc, char** argv){
    setlocale(LC_ALL, "C.UTF-8");
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter{};
    std::list<std::u32string> args;
    for(int idx = 0; idx < argc; idx++)
        args.push_back(converter.from_bytes(argv[idx]));
    auto native_args = basic_std::convert_args(args);
    basic_std::Main(native_args.data(), argc);
    return 0;
}