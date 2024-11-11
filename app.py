from flask import Flask, render_template, request, url_for, session
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.stats import t

app = Flask(__name__)
app.secret_key = "supersecretkey12345"  # Replace with your own secret key, needed for session management


def generate_data(N, mu, beta0, beta1, sigma2, S):
    # Generate data and initial plots

    # TODO 1: Generate a random dataset X of size N with values between 0 and 1
    X = np.random.rand(N)  # Replace with code to generate random values for X

    # TODO 2: Generate a random dataset Y using the specified beta0, beta1, mu, and sigma2
    # Y = beta0 + beta1 * X + mu + error term
    error = np.random.normal(0, sigma2, N)
    Y = beta0 + beta1 * X + mu + error # Replace with code to generate Y

    # TODO 3: Fit a linear regression model to X and Y
    model = LinearRegression()
    model.fit(X.reshape(-1, 1), Y)
    slope = model.coef_[0]  # Extract the slope (coefficient) from the fitted model
    intercept = model.intercept_  # Extract the intercept from the fitted model

    # TODO 4: Generate a scatter plot of (X, Y) with the fitted regression line
    plot1_path = "static/plot1.png"
    # Replace with code to generate and save the scatter plot
    plt.figure()
    plt.scatter(X, Y, color="blue", alpha=0.5, label="Data points")
    plt.plot(X, slope * X + intercept, color="red", label=f"Fitted line: Y = {intercept:.2f} + {slope:.2f}X")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.savefig(plot1_path)  # Save the scatter plot
    plt.close()

    # TODO 5: Run S simulations to generate slopes and intercepts
    slopes = []
    intercepts = []

    for _ in range(S):
        # TODO 6: Generate simulated datasets using the same beta0 and beta1
        X_sim = np.random.rand(N)  # Replace with code to generate simulated X values
        error_sim = np.random.normal(0, np.sqrt(sigma2), N)
        Y_sim = beta0 + beta1 * X_sim + mu + error_sim  # Replace with code to generate simulated Y values

        # TODO 7: Fit linear regression to simulated data and store slope and intercept
        sim_model = LinearRegression()
        sim_model.fit(X_sim.reshape(-1, 1), Y_sim)
        sim_slope = sim_model.coef_[0]  # Extract slope from sim_model
        sim_intercept = sim_model.intercept_  # Extract intercept from sim_model

        slopes.append(sim_slope)
        intercepts.append(sim_intercept)

    # TODO 8: Plot histograms of slopes and intercepts
    plot2_path = "static/plot2.png"
    # Replace with code to generate and save the histogram plot
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.hist(slopes, bins=20, color="skyblue", edgecolor="black", alpha=0.7)
    plt.axvline(slope, color="red", linestyle="--", label=f"Observed slope: {slope:.4f}")
    plt.xlabel("Slope")
    plt.ylabel("Frequency")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.hist(intercepts, bins=20, color="lightcoral", edgecolor="black", alpha=0.7)
    plt.axvline(intercept, color="red", linestyle="--", label=f"Observed intercept: {intercept:.4f}")
    plt.xlabel("Intercept")
    plt.ylabel("Frequency")
    plt.legend()

    plt.savefig(plot2_path)  # Save the histogram plot
    plt.close()

    # TODO 9: Return data needed for further analysis, including slopes and intercepts
    # Calculate proportions of slopes and intercepts more extreme than observed
    slope_more_extreme = np.mean([1 if abs(s) >= abs(slope) else 0 for s in slopes])  # Replace with code to calculate proportion of slopes more extreme than observed
    intercept_extreme = np.mean([1 if abs(i) >= abs(intercept) else 0 for i in intercepts])  # Replace with code to calculate proportion of intercepts more extreme than observed

    # Return data needed for further analysis
    return (
        X,
        Y,
        slope,
        intercept,
        plot1_path,
        plot2_path,
        slope_more_extreme,
        intercept_extreme,
        slopes,
        intercepts,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        N = int(request.form["N"])
        mu = float(request.form["mu"])
        sigma2 = float(request.form["sigma2"])
        beta0 = float(request.form["beta0"])
        beta1 = float(request.form["beta1"])
        S = int(request.form["S"])

        # Generate data and initial plots
        (
            X,
            Y,
            slope,
            intercept,
            plot1,
            plot2,
            slope_extreme,
            intercept_extreme,
            slopes,
            intercepts,
        ) = generate_data(N, mu, beta0, beta1, sigma2, S)

        # Store data in session
        session["X"] = X.tolist()
        session["Y"] = Y.tolist()
        session["slope"] = slope
        session["intercept"] = intercept
        session["slopes"] = slopes
        session["intercepts"] = intercepts
        session["slope_extreme"] = slope_extreme
        session["intercept_extreme"] = intercept_extreme
        session["N"] = N
        session["mu"] = mu
        session["sigma2"] = sigma2
        session["beta0"] = beta0
        session["beta1"] = beta1
        session["S"] = S

        # Return render_template with variables
        return render_template(
            "index.html",
            plot1=plot1,
            plot2=plot2,
            slope_extreme=slope_extreme,
            intercept_extreme=intercept_extreme,
            N=N,
            mu=mu,
            sigma2=sigma2,
            beta0=beta0,
            beta1=beta1,
            S=S,
        )
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # This route handles data generation (same as above)
    return index()


@app.route("/hypothesis_test", methods=["POST"])
def hypothesis_test():
    # Retrieve data from session
    N = int(session.get("N"))
    S = int(session.get("S"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))

    parameter = request.form.get("parameter")
    test_type = request.form.get("test_type")

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        simulated_stats = np.array(slopes)
        observed_stat = slope
        hypothesized_value = beta1
    else:
        simulated_stats = np.array(intercepts)
        observed_stat = intercept
        hypothesized_value = beta0

    # TODO 10: Calculate p-value based on test type
    if test_type == ">":
        # Greater than test
        p_value = np.sum(simulated_stats >= observed_stat) / S
    elif test_type == "<":
        # Less than test
        p_value = np.sum(simulated_stats <= observed_stat) / S
    elif test_type == "!=":
        # Not equal to test
        p_value = np.sum(np.abs(simulated_stats-hypothesized_value) >= abs(observed_stat-hypothesized_value)) / S
    else:
        p_value = None  # In case of an invalid test type

    # TODO 11: If p_value is very small (e.g., <= 0.0001), set fun_message to a fun message
    fun_message = None
    if p_value is not None and p_value <= 0.0001:
        fun_message = (
            "Incredible! You've encountered an exceptionally rare event! "
            "With a p-value this small, it’s almost as if the universe is trying to tell you something significant!"
        )

    # TODO 12: Plot histogram of simulated statistics
    plot3_path = "static/plot3.png"
    # Replace with code to generate and save the plot
    plt.figure()
    plt.hist(simulated_stats, bins=20, color="lightblue", edgecolor="black", alpha=0.7, label="Simulated Statistics")
    plt.axvline(observed_stat, color="red", linestyle="--", linewidth=2, label=f"Observed {parameter.capitalize()}: {observed_stat:.4f}")
    plt.axvline(hypothesized_value, color="blue", linestyle="-", linewidth=2, label=f"Hypothesized {parameter.capitalize()} (H₀): {hypothesized_value}")
    plt.xlabel(parameter.capitalize())
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(plot3_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot3=plot3_path,
        parameter=parameter,
        observed_stat=observed_stat,
        hypothesized_value=hypothesized_value,
        N=N,
        beta0=beta0,
        beta1=beta1,
        S=S,
        # TODO 13: Uncomment the following lines when implemented
        p_value=p_value,
        fun_message=fun_message,
    )

@app.route("/confidence_interval", methods=["POST"])
def confidence_interval():
    # Retrieve data from session
    N = int(session.get("N"))
    mu = float(session.get("mu"))
    sigma2 = float(session.get("sigma2"))
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))
    S = int(session.get("S"))
    X = np.array(session.get("X"))
    Y = np.array(session.get("Y"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")

    parameter = request.form.get("parameter")
    confidence_level = float(request.form.get("confidence_level"))

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        estimates = np.array(slopes)
        observed_stat = slope
        true_param = beta1
    else:
        estimates = np.array(intercepts)
        observed_stat = intercept
        true_param = beta0

    # TODO 14: Calculate mean and standard deviation of the estimates

    mean_estimate = np.mean(estimates)
    std_estimate = np.std(estimates, ddof=1)

    # TODO 15: Calculate confidence interval for the parameter estimate
    # Use the t-distribution and confidence_level
    # Calculate the critical value for the confidence interval
    # Calculate the critical t-value
    alpha = 1 - confidence_level / 100
    t_critical = t.ppf(1 - alpha / 2, df = N - 1)
    margin_of_error = t_critical * (std_estimate / np.sqrt(N))
    # Calculate the confidence interval
    ci_lower = mean_estimate - margin_of_error
    ci_upper = mean_estimate + margin_of_error

    # TODO 16: Check if confidence interval includes true parameter
    includes_true = ci_lower <= true_param <= ci_upper

    # TODO 17: Plot the individual estimates as gray points and confidence interval
    # Plot the mean estimate as a colored point which changes if the true parameter is included
    # Plot the confidence interval as a horizontal line
    # Plot the true parameter value
    plot4_path = "static/plot4.png"
    # Write code here to generate and save the plot
    # Visualization
    plt.figure(figsize=(10, 5))
    # Plot individual simulated estimates
    plt.scatter(estimates, [1] * len(estimates), color="gray", alpha=0.5, label="Simulated Estimates")

    # Plot the mean estimate, color-coded based on whether it includes the true parameter
    mean_color = "green" if includes_true else "red"
    plt.scatter([mean_estimate], [1], color=mean_color, s=100, label=f"Mean Estimate (includes true param)" if includes_true else "Mean Estimate (excludes true param)")

    # Plot the confidence interval as a horizontal line
    plt.hlines(1, ci_lower, ci_upper, color="blue", linewidth=2, label=f"{confidence_level*100}% Confidence Interval")

    # Mark the true parameter value
    plt.axvline(true_param, color="purple", linestyle="--", label=f"True {parameter.capitalize()} Value: {true_param}")

    # Additional plot settings
    plt.xlabel(parameter.capitalize())
    plt.yticks([])
    plt.legend(loc="upper left")

    plt.savefig(plot4_path)
    plt.close()


    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot4=plot4_path,
        parameter=parameter,
        confidence_level=confidence_level,
        mean_estimate=mean_estimate,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        includes_true=includes_true,
        observed_stat=observed_stat,
        N=N,
        mu=mu,
        sigma2=sigma2,
        beta0=beta0,
        beta1=beta1,
        S=S,
    )


if __name__ == "__main__":
    app.run(debug=True)
