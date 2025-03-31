
---
date: 2024-12-22 17:08
description: At the 2019 WWDC Apple introduced a new UI framework called SwiftUI. From the initial phase of iOS development, we are looking at Xibs and storyboards to build a user interface in ios, macOS and WatchOS app, many more developers were fed-up from developing UI by Storyboard, maybe you are one of them, there are a lot of drawbacks of UIkit over SwiftUI.
tags: first, article
---
# Result In Swift

Apple introduced Result standard library into Swift Codebase in swift 5, Result has enum type, Result represents the outcome of any Operation or Functionality, like calling asynchronous API call, API response may be Success or failure, We can use Result to represent the combination of API Success and Fail. Let us see how Result works, this is how Result defined in Swift library
```swift
enum Result<Success, Failure> where Failure: Error {
    case success(Success)
    case failure(Failure)
}
```
Result returns either success or failure with value. Success type is generic means it could be anything Array of model objects like [Employee] more may be NSData, String, Int, but failure should always conform Error Type. Syntax be like
```swift
Result <[Employee]?, Error>
```
<h4>Lets Implement Result Practically </h4>

We looked around how Results defined in Swift library, Now we will perform Result type implementation by calling asynchronous API.

Here, I have created one model class, it conforms decodable protocol for the sake of decode response received from web service without parsing it by any particular key from the response. if you didn’t get this don’t worry as we will move on, you will get to know why this model class we have created. Here is the example of the model class.

```swift
struct Employee: Decodable {
    var id: Int?
    var first_name : String?
    var last_name: String?
    var email: String?
    var avatar: String?
}

```
As we have discussed Result represents two combinations of the parameter, which are Success and Failure, Success type could be anything model, string, int but Failure should always conform Error type.

After calling API outcome may be a failure, which will come in front in the form of Error type, Here we are trying to categorize this error by creating APIErrors enum to segregate which type of failure we faced while calling asynchronous API Call, Error may be Url not found, parsing fails, or it could be data missing Error. we have created this enum for readability and understanding purpose to know the cause of the error, You can ignore this part if you want to move on with only basic Error type.

```swift
enum APIErrors: Error {
    case URLNotFoundError
    case ParsingError
    case DataMissingError
}

```
Now, we are in an important phase, keep your eyes on each line. previously we are handling API outcomes ( success and failure ) by adding two parameters in the completion handler to get response results. for example :
```swift
func getEmployeeData(completionHandler: @escaping ([Employee]?, Error?) -> Void) {
    ...
}

```
Since we were checking previously is error is nil, we were considering the API called is successful. and we were handling responses like [Employee] model array data.

Now we changed a few things in completion handler callback, we wrapped both parameters in the Result type.

```swift
func getEmployeeData(completionHandler: @escaping(Result <[Employee]?, APIErrors>) -> Void ) {
}
```
So Results can send either success or failure to completion handler. if the response will have a successful outcome, Result in returns with any data and if the response will have failure outcome Result in returns with Error type.

<h4>Result returns success :</h4>
```swift
let employeeObjects = try JSONDecoder.init().decode([Employee].self, from: jsonData)
completionHandler(.success(employeeObjects))
```

<h4>Result returns failure :</h4>
```swift
completionHandler(.failure(.ParsingError))
```

I have created one demo function for the asynchronous API call. I am calling free open-source API and getting employee data, we have already created a model class for handling response. here I conveyed how Result type is responding on API outcome, Outcome may be success or failure, we are returning an Array of Employee objects on success and APIError enum error type on failure. Please look carefully at this bunch of code. I tried my best to convey Result type functioning.

```swift
func getEmployeeData(completionHandler: @escaping(Result <[Employee]?, APIErrors>) -> Void ) {
        let urlString = "https://reqres.in/api/users?"
        guard let url = URL(string: urlString) else {
            print("Invalid url")
            return
        }
        URLSession.shared.dataTask(with: url) { (responseData, responseInfo, error) in
            if error == nil {
                do {
                    let jsonResponse = try JSONSerialization.jsonObject(with: responseData!, options: .mutableContainers)
                    if let responseArray = jsonResponse as? [String:Any] {
                        if let dataArray = responseArray["data"] as? [[String:Any]] {
                            do {
                                let jsonData = try JSONSerialization.data(withJSONObject: dataArray, options: .fragmentsAllowed)
                                let employeeObjects = try JSONDecoder.init().decode([Employee].self, from: jsonData)
                                completionHandler(.success(employeeObjects))
                            } catch  {
                                completionHandler(.failure(.ParsingError))
                            }
                        }
                    }
                } catch {
                    completionHandler(.failure(.DataMissingError))
                }
            } else {
                completionHandler(.failure(.URLNotFoundError))
            }
        }.resume()
    }
```

Now we almost have done everything, implement completion handler wherever you want, Switch Result into .success and .failure block, you will also get success parameter you sent from function itself, as success will return Array of employee objects and failure will return Error type.

```swift
var emps = [Employee]()
    init() {
        getEmployeeData { (result) in
            switch result {
            case  .success(let employees):
                self.emps = employees!
                break
            case  .failure(let error):
                print(error.localizedDescription)
                break
            }
        }
    }

```

I have tried all this code and then added on the blog post, if somebody is not understood anything, please write me an email, I will reply on the same, and If you face anything went wrong in code or explanation please let me know.

email: blogswithrahul@gmail.com

<h4>Conclusion :</h4>
A feature like a Result eliminated lots of uncertainty in the code, Result can be used for handling outcome and states of any logical functionality and critical operations.
<!-- AdSense Code -->
<div style="text-align:center;">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-9268892677399703"
       data-ad-slot="1234567890"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>
       (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
