import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.graph_objects as go
import os

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Maternal Mortality Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .chart-section {
        margin-bottom: 2.5rem;
    }
    .writeup-box {
        background-color: #f8f9fa;
        border-left: 4px solid #4f46e5;
        padding: 1rem 1.25rem;
        border-radius: 0.375rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        color: #374151;
    }
    @media (prefers-color-scheme: dark) {
        .writeup-box {
            background-color: #1e293b;
            border-left: 4px solid #818cf8;
            color: #e2e8f0;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("Is There a Safest Age to Give Birth? What US Mortality Data Says")
st.caption("This dashboard tells the story of women who have fallen through the cracks of the US's maternal mortality crisis — a crisis that, the data shows, has only worsened over time, with women over 40 facing a mortality rate roughly 4X the national average. Throughout this exploration, mortality rate is communicated as deaths per 100,000 live births. The dashboard traces maternal mortality alongside the number of live births and deaths recorded each year, spanning January 2019 through March 2026. ")
st.markdown("---")

# --- DATA GENERATION ---
@st.cache_data
def generate_data():
    np.random.seed(42)

    # 1. Bar Chart Data (CSV Processing)
    age_subgroup = pd.read_csv("age_subgroup.csv")
        
    df_filtered = age_subgroup[age_subgroup["subgroup"] != "Total"]
    categories = df_filtered["subgroup"].iloc[0:3]
    performance = df_filtered["maternal_mortality_rate"].iloc[0:3]
    
    df_bar = pd.DataFrame({'Subgroup': categories, 'MMR': performance})
    target_value = age_subgroup["maternal_mortality_rate"].iloc[3]
    
    # 2. Heatmap Data
    maternal_mortality_age = pd.read_csv("maternal_mortality_age.csv")
    
    # 3. Pie Chart Data
    df_filtered = age_subgroup[age_subgroup["subgroup"] != "Total"]
    
    # 4. Distribution Data
    mmr_age_40 = pd.read_csv("mmr_age_40.csv")
    mean_val = mmr_age_40['maternal_mortality_rate'].mean()
    mmr_age_40['deviation'] = mmr_age_40['maternal_mortality_rate'] - mean_val

    std_val = mmr_age_40['maternal_mortality_rate'].std()
    mmr_age_40['z_score'] = (mmr_age_40['maternal_mortality_rate'] - mean_val) / std_val
    
    # 5. Animated Line Chart Data
    df = maternal_mortality_age.copy()
    df["month_end_date"] = pd.to_datetime(df["month_end_date"])
    df["month_str"] = df["month_end_date"].dt.strftime("%Y-%m")
    df = df.sort_values("month_end_date")

    # --- Return everything needed for the plot ---
    return df_bar, target_value, maternal_mortality_age,  df_filtered , mmr_age_40, df

df_bar, target_value, maternal_mortality_age,  df_filtered , mmr_age_40, df = generate_data()


# 1. BAR GRAPH (MATPLOTLIB IN STREAMLIT)
with st.container():
    st.subheader("Maternal Mortality Rate (Per Age Group) vs Average")

    left, center, right = st.columns([1, 3, 1])
    with center:
        fig_bar = px.bar(
            df_bar,
            x="Subgroup",
            y="MMR",
            color="Subgroup",
            text_auto=".2s",
            title=None,
        )
        fig_bar.add_hline(
            y=target_value,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average MMR across age groups: {target_value:.2f}",
            annotation_position="top left",
        )
        fig_bar.update_layout(showlegend=False, height=420)
        st.plotly_chart(fig_bar, width='stretch')

    st.markdown(f"""
        <div class="writeup-box">
            <strong> </strong> This bar graph shows the average maternal mortality rate (MMR) for each age group compared to the national average (calculated across under 25, 25–39, and 40 and over groups). It confirms that women over 40 face a disproportionately high risk, with an MMR of 82.07 per 100,000 live births — about <strong>4x</strong> the national average of <strong>{target_value:.2f}</strong>.
    """, unsafe_allow_html=True)

st.divider()

# 3. HEATMAP (MMR by Year/Month, per Age Subgroup)

with st.container():
    st.subheader("Maternal Mortality Rate by Month and Age Group")

    age_groups = maternal_mortality_age["subgroup"].unique()
    n = len(age_groups)

    vmin = maternal_mortality_age["maternal_mortality_rate"].min()
    vmax = maternal_mortality_age["maternal_mortality_rate"].max()

    cols = st.columns(n)

    for col, age in zip(cols, age_groups):
        with col:
            subset = maternal_mortality_age[
                maternal_mortality_age["subgroup"] == age
            ]
            pivot = subset.pivot(
                index="death_yr",
                columns="death_month",
                values="maternal_mortality_rate",
            )

            fig_heat = px.imshow(
                pivot,
                zmin=vmin,
                zmax=vmax,
                text_auto=".0f",
                aspect="auto",
                labels=dict(x="Month", y="Year", color="MMR"),
                title=age,
                color_continuous_scale="Tealrose",
            )
        fig_heat.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))

        st.plotly_chart(fig_heat, width='stretch')

st.markdown(""" 
    <div class="writeup-box">
        This heatmap shows maternal mortality rate patterns by year and month for each age subgroup, 
        with color scaled by each group's minimum and maximum MMR. The 40-and-over group stands out as 
        markedly darker than the other two — further confirmation of its substantially higher risk. Several months for this group approach or exceed 100 deaths per 100,000 live births."
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 2. PIE CHART
with st.container():
    st.subheader("Share of Total Births by Age Group")

    left, center, right = st.columns([1, 2, 1])
    with center:
        fig_pie = px.pie(
            df_filtered, values='total_births', names='subgroup', hole=0.4
        )
        fig_pie.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_pie, width='stretch')

    st.markdown("""
        <div class="writeup-box">
            <strong>To further contextualize the mortality rates across age groups, this pie chart shows the percentage of live births 
            and the percentage of maternal deaths that each age group accounts for. Women 40 and over make up
            only about 4% of live births, yet account for <strong>4x</strong> the average maternal mortality rate.
            By contrast, the 25–39 age group accounts for the largest share of live births, so a similar number of deaths has a smaller proportional impact on their overall rate.
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 3. DISTRIBUTION PLOT (CENTERED)
with st.container():
    st.subheader("Distribution of Maternal Mortality Rates, Ages 40+")
    
lleft, center, right = st.columns([1, 3, 1])
with center:
    fig_dist, ax_dist = plt.subplots(figsize=(8, 5))
    fig_dist.patch.set_alpha(0.0)
    ax_dist.set_facecolor('none')

    
    sns.histplot(
        mmr_age_40['deviation'],
        kde=True,
        color='#FFA0A0',   
        alpha=1.0,         
        edgecolor='black', 
        linewidth=1.0,
        ax=ax_dist,
    )
    
    if ax_dist.lines:
        kde_line = ax_dist.lines[0]
        kde_line.set_color('white')
        kde_line.set_linewidth(2)
        kde_line.set_zorder(5)

    # Mean line
    ax_dist.axvline(0, color='red', linestyle='--', label='Mean (0)', zorder=6)

    axis_color = 'white'
    ax_dist.set_title('Mortality Distribution Plot (40 years old and over)', color=axis_color)
    ax_dist.set_xlabel('Distance from Mean', color=axis_color)
    ax_dist.set_ylabel('Count', color=axis_color)
    ax_dist.tick_params(colors=axis_color)
    
    # Legend with frame disabled
    legend = ax_dist.legend(frameon=False)
    for text in legend.get_texts():
        text.set_color(axis_color)

    for spine in ax_dist.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    st.pyplot(fig_dist, width='stretch', transparent=True)
 
    
    st.markdown("""
        <div class="writeup-box">
            This distribution plot shows the maternal mortality rate for women 
            40 and over across the six years between 2019 and 2026, examining whether the rate has 
            remained consistent over time. As the graph shows, the values follow a roughly normal 
            distribution, suggesting the rate fluctuates within a relatively stable range rather than 
            trending sharply up or down.
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 4. ANIMATED LINE GRAPH (BOTTOM CENTER)
with st.container():
    st.subheader("Maternal Mortality Rate Over Time by Age Group")
    line_pivot = (
        df.pivot_table(
            index="month_end_date",
            columns="subgroup",
            values="maternal_mortality_rate",
            aggfunc="first",
        )
        .sort_index()
    )

    notebook_order = ["25-39 years", "40 years and over", "Under 25 years"]
    age_categories = [
        subgroup for subgroup in notebook_order if subgroup in line_pivot.columns
    ]
    months = pd.DatetimeIndex(line_pivot.index)

    if months.empty or not age_categories:
        st.warning("No monthly age-subgroup data is available for the animation.")
    else:
        window = 18
        frame_duration_ms = 150
        colors = px.colors.qualitative.Plotly
        color_by_category = {
            category: colors[i % len(colors)]
            for i, category in enumerate(age_categories)
        }

        def traces_for_frame(frame_index):
            current_month = months[frame_index]
            visible_through_current = months[: frame_index + 1]

            line_traces = []
            current_point_traces = []

            for category in age_categories:
                category_color = color_by_category[category]
                current_rate = line_pivot.loc[current_month, category]

                line_traces.append(
                    go.Scatter(
                        x=visible_through_current,
                        y=line_pivot.loc[visible_through_current, category],
                        mode="lines+markers",
                        name=category,
                        legendgroup=category,
                        line=dict(color=category_color, width=2.5),
                        marker=dict(size=5, color=category_color),
                        hovertemplate=(
                            f"<b>{category}</b><br>"
                            "%{x|%B %Y}<br>"
                            "MMR: %{y:.1f}<extra></extra>"
                        ),
                    )
                )

                current_point_traces.append(
                    go.Scatter(
                        x=[current_month],
                        y=[current_rate],
                        mode="markers",
                        name=f"{category} current point",
                        legendgroup=category,
                        showlegend=False,
                        marker=dict(
                            size=12,
                            color=category_color,
                            line=dict(color="black", width=1.5),
                        ),
                        hovertemplate=(
                            f"<b>{category}</b><br>"
                            "%{x|%B %Y}<br>"
                            "Current MMR: %{y:.1f}<extra></extra>"
                        ),
                    )
                )

       
            return line_traces + current_point_traces

        def x_axis_range(frame_index):
            start_index = max(0, frame_index - window + 1)
            # Give the first frame a non-zero date range.
            end_index = min(
                len(months) - 1,
                max(frame_index, start_index + 1),
            )
            return [months[start_index], months[end_index]]

        frame_names = [month.strftime("%Y-%m-%d") for month in months]
        animation_frames = []

        for frame_index, current_month in enumerate(months):
            animation_frames.append(
                go.Frame(
                    name=frame_names[frame_index],
                    data=traces_for_frame(frame_index),
                    layout=go.Layout(
                        title=dict(
                            text=(
                                "Maternal Mortality Rate (MMR) Per Age : "
                                f"{current_month.strftime('%B %Y')}"
                            ),
                            x=0.5,
                            xanchor="center",
                        ),
                        xaxis=dict(range=x_axis_range(frame_index)),
                    ),
                )
            )

        initial_title = (
            "Maternal Mortality Rate (MMR) Per Age : "
            f"{months[0].strftime('%B %Y')}"
        )
        max_rate = float(line_pivot[age_categories].max().max())

        fig_line = go.Figure(
            data=animation_frames[0].data,
            frames=animation_frames,
        )
        fig_line.update_layout(
            title=dict(text=initial_title, x=0.5, xanchor="center"),
            height=520,
            margin=dict(l=35, r=25, t=75, b=125),
            xaxis=dict(
                title="Month (As of End Date)",
                type="date",
                range=x_axis_range(0),
                dtick="M1",
                tickformat="%b %Y",
                tickangle=-45,
            ),
            yaxis=dict(
                title="Mortality rate (per 100k births)",
                range=[0, max_rate * 1.1],
                fixedrange=False,
            ),
            legend=dict(
                title="Age subgroup",
                x=0.01,
                y=0.99,
                xanchor="left",
                yanchor="top",
            ),
            hovermode="closest",
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0.0,
                    y=-0.24,
                    xanchor="left",
                    yanchor="top",
                    showactive=False,
                    buttons=[
                        dict(
                            label="▶ Play",
                            method="animate",
                            args=[
                                None,
                                dict(
                                    mode="immediate",
                                    fromcurrent=True,
                                    transition=dict(duration=0),
                                    frame=dict(
                                        duration=frame_duration_ms,
                                        redraw=True,
                                    ),
                                ),
                            ],
                        ),
                        dict(
                            label="⏸ Pause",
                            method="animate",
                            args=[
                                [None],
                                dict(
                                    mode="immediate",
                                    transition=dict(duration=0),
                                    frame=dict(duration=0, redraw=False),
                                ),
                            ],
                        ),
                    ],
                )
            ],
            sliders=[
                dict(
                    active=0,
                    x=0.20,
                    y=-0.19,
                    len=0.78,
                    xanchor="left",
                    yanchor="top",
                    currentvalue=dict(prefix="Month: ", visible=True),
                    transition=dict(duration=0),
                    steps=[
                        dict(
                            label=month.strftime("%b %Y"),
                            method="animate",
                            args=[
                                [frame_names[frame_index]],
                                dict(
                                    mode="immediate",
                                    transition=dict(duration=0),
                                    frame=dict(duration=0, redraw=True),
                                ),
                            ],
                        )
                        for frame_index, month in enumerate(months)
                    ],
                )
            ],
        )

        left, center, right = st.columns([1, 5, 1])
        with center:
            st.plotly_chart(fig_line, width='stretch')

        st.markdown(
            f"""
            <div class="writeup-box">
                </strong> Press <strong>Play</strong> to follow the three age-subgroup mortality-rate series month by month. The chart displays a rolling {window}-month window, enlarges each subgroup's latest observation, and updates the title to the active month. For most of the six years, the under-25 and 25–39 age groups have remained fairly consistent, tracking closely together and reflecting a similar level of risk. The 40-and-over group, by contrast, consistently experiences maternal mortality rates far higher than the other two. One notable pattern is a rise in rates around 2021–2022, which may reflect the impact of the COVID-19 pandemic on maternal health, reporting, or data collection during that period.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.container():
        st.subheader("Conclusion: ")

        st.markdown(
        f"""
            <div class="writeup-box">
            The story this dashboard tells is one of contradiction: women 40 and over make up only about 4% of live births, yet face a maternal mortality rate roughly <strong>4x</strong> the national average. Fewer births should mean fewer chances for something to go wrong; instead, this group carries the highest risk of all. The pattern held steady across six years, with a notable rise around 2021–2022 coinciding with the COVID-19 pandemic. These numbers represent women who chose to become mothers later in life, only to face risks far greater than their younger peers. This risk reflects real, addressable gaps in how the healthcare system supports older mothers.
            Closing this gap starts with ideas such as expanding access to high-risk obstetric care, strengthening postpartum care, and ensuring providers flag age-related risk factors before complications arise. We have the data — now we have to turn ideas into action.
            </div>
        """,
    unsafe_allow_html=True,
        )